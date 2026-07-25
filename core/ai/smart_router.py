import asyncio
import logging
from typing import Any, Callable, List

from core.config.settings import settings

logger = logging.getLogger("jobhunterai.smart_router")


async def route(primary_fn: Callable, fallback_fn: Callable, *args, **kwargs) -> Any:
    """
    Dual-Engine Router:
    1. Checks for required environment variables for primary_fn.
       Supports AND (list) and OR (nested list) logic.
    2. Attempts primary_fn (Tier 1 - Cloud).
    3. If fails or keys missing, attempts fallback_fn (Tier 3 - Local).
    """
    # 1. Check required environment variables using standardized settings
    required_envs: List[Any] = getattr(primary_fn, "required_envs", [])

    can_proceed = True
    missing_info = []

    # Get settings as dict for easy access
    config_dict = settings.model_dump()

    for requirement in required_envs:
        if isinstance(requirement, list):
            # OR Logic: At least one in the sub-list must exist
            if not any(config_dict.get(env) for env in requirement):
                can_proceed = False
                missing_info.append(f"({' or '.join(requirement)})")
        else:
            # AND Logic: Must exist
            if not config_dict.get(requirement):
                can_proceed = False
                missing_info.append(requirement)

    if not can_proceed:
        logger.warning(
            f"Missing Tier 1 API keys {', '.join(missing_info)}. Falling back to Tier 3 (Local) for {primary_fn.__name__}."
        )
        result = fallback_fn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result

    # 2. Attempt primary cloud function
    try:
        logger.info(f"Initiating Tier 1 (Cloud) call for {primary_fn.__name__}...")
        result = primary_fn(*args, **kwargs)
        if asyncio.iscoroutine(result) or asyncio.iscoroutinefunction(primary_fn):
            result = await result

        if result is None:
            logger.error(
                f"Tier 1 (Cloud) for {primary_fn.__name__} returned None. Falling back to Tier 3 (Local)."
            )
            result = fallback_fn(*args, **kwargs)
            if asyncio.iscoroutine(result) or asyncio.iscoroutinefunction(fallback_fn):
                return await result
            return result

        logger.info(f"Tier 1 (Cloud) for {primary_fn.__name__} completed successfully.")
        return result

    except Exception as e:
        err_str = str(e).lower()
        if "safety" in err_str or "policy" in err_str:
            logger.error(f"Tier 1 (Cloud) blocked by AI Safety Filter: {str(e)}")
        else:
            logger.error(
                f"Tier 1 (Cloud) call failed for {primary_fn.__name__} with exception: {str(e)}"
            )

        logger.info(f"Falling back to Tier 3 (Local) for {primary_fn.__name__}.")

        # 3. Execute fallback
        try:
            result = fallback_fn(*args, **kwargs)
            if asyncio.iscoroutine(result) or asyncio.iscoroutinefunction(fallback_fn):
                return await result
            return result
        except Exception as fe:
            logger.critical(
                f"Tier 3 (Local) for {primary_fn.__name__} ALSO failed: {str(fe)}"
            )
            # Return safe placeholder defined on the fallback function or a generic empty dict
            return getattr(fallback_fn, "safe_placeholder", {})
