import asyncio
import inspect
import logging
from typing import Any, Callable, List

from core.config.settings import settings

logger = logging.getLogger("jobhunterai.smart_router")


def _is_api_key_set(config_dict: dict, key: str) -> bool:
    """Check if an API key is actually set (not None, not empty, not whitespace)."""
    val = config_dict.get(key)
    return val is not None and str(val).strip() != ""


def _check_required_envs(required_envs: List[Any], config_dict: dict) -> bool:
    """
    Validates required environment variables with AND/OR logic.
    - list of strings: all must be set (AND)
    - list of lists: at least one sub-list must be satisfied (OR)
    """
    for requirement in required_envs:
        if isinstance(requirement, list):
            # OR Logic: At least one in the sub-list must exist
            if not any(_is_api_key_set(config_dict, env) for env in requirement):
                return False
        else:
            # AND Logic: Must exist
            if not _is_api_key_set(config_dict, requirement):
                return False
    return True


async def route(*tier_functions: Callable, **kwargs) -> Any:
    """
    N-Tier Multi-Engine Router.
    Sequentially attempts each tier function until one succeeds or all fail.

    1. Checks required environment variables for each tier.
    2. Executes tier (handles sync/async).
    3. Falls back to next tier on None return or exception.
    """
    config_dict = settings.model_dump()
    last_tier_result = None

    for i, tier_fn in enumerate(tier_functions):
        tier_name = tier_fn.__name__
        logger.info(f"Attempting Tier {i+1}: {tier_name}...")

        # 1. Check requirements
        required_envs = getattr(tier_fn, "required_envs", [])
        if not _check_required_envs(required_envs, config_dict):
            logger.warning(f"Tier {i+1} ({tier_name}) skipped: Missing required API keys.")
            continue

        # 2. Execute tier
        try:
            if inspect.iscoroutinefunction(tier_fn):
                result = await tier_fn(**kwargs)
            else:
                result = tier_fn(**kwargs)

            # If sync function returned a coroutine (unlikely with decorator but good to check)
            if asyncio.iscoroutine(result):
                result = await result

            if result is not None:
                logger.info(f"Tier {i+1} ({tier_name}) succeeded.")
                return result

            logger.warning(f"Tier {i+1} ({tier_name}) returned None. Falling back...")
            last_tier_result = getattr(tier_fn, "safe_placeholder", None)

        except Exception as e:
            err_str = str(e).lower()
            if "safety" in err_str or "policy" in err_str:
                logger.error(f"Tier {i+1} blocked by AI Safety Filter: {str(e)}")
            elif "quota" in err_str or "rate limit" in err_str:
                logger.error(f"Tier {i+1} failed: Rate limit exceeded.")
            else:
                logger.error(f"Tier {i+1} ({tier_name}) failed with exception: {str(e)}")

            last_tier_result = getattr(tier_fn, "safe_placeholder", None)
            continue

    logger.critical("All AI tiers exhausted. Returning safe placeholder.")
    return last_tier_result or {"error": "All providers failed"}
