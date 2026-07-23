import os
import logging
from typing import Callable, Any, List

import asyncio

logger = logging.getLogger("jobhunterai.smart_router")

async def route(primary_fn: Callable, fallback_fn: Callable, *args, **kwargs) -> Any:
    """
    Dual-Engine Router:
    1. Checks for required environment variables for primary_fn.
       Supports AND (list) and OR (nested list) logic.
    2. Attempts primary_fn (Tier 1 - Cloud).
    3. If fails or keys missing, attempts fallback_fn (Tier 3 - Local).
    """
    # 1. Check required environment variables
    required_envs: List[Any] = getattr(primary_fn, "required_envs", [])

    can_proceed = True
    missing_info = []

    for requirement in required_envs:
        if isinstance(requirement, list):
            # OR Logic: At least one in the sub-list must exist
            if not any(os.getenv(env) for env in requirement):
                can_proceed = False
                missing_info.append(f"({' or '.join(requirement)})")
        else:
            # AND Logic: Must exist
            if not os.getenv(requirement):
                can_proceed = False
                missing_info.append(requirement)

    if not can_proceed:
        logger.warning(f"Missing Tier 1 API keys {', '.join(missing_info)}. Falling back to Tier 3 (Local) for {primary_fn.__name__}.")
        result = fallback_fn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result

    # 2. Attempt primary cloud function
    try:
        logger.info(f"Initiating Tier 1 (Cloud) call for {primary_fn.__name__}...")
        result = primary_fn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result

        if result is None:
            logger.error(f"Tier 1 (Cloud) for {primary_fn.__name__} returned None. Falling back to Tier 3 (Local).")
            result = fallback_fn(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result

        logger.info(f"Tier 1 (Cloud) for {primary_fn.__name__} completed successfully.")
        return result

    except Exception as e:
        logger.error(f"Tier 1 (Cloud) for {primary_fn.__name__} failed with exception: {str(e)}")
        logger.info(f"Falling back to Tier 3 (Local) for {primary_fn.__name__}.")

        # 3. Execute fallback
        try:
            result = fallback_fn(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result
        except Exception as fe:
            logger.critical(f"Tier 3 (Local) for {primary_fn.__name__} ALSO failed: {str(fe)}")
            # Return safe placeholder defined on the fallback function or a generic empty dict
            return getattr(fallback_fn, "safe_placeholder", {})
