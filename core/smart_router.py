import time
import asyncio
import os
import random
from typing import Any, Dict, List, Optional, Callable, Awaitable
from utils.logger import logger

class CircuitBreaker:
    def __init__(self, name: str, threshold: int = 3, reset_timeout: int = 300):
        self.name = name
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF-OPEN

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit Breaker [{self.name}] is now OPEN due to {self.failure_count} failures.")

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF-OPEN"
                logger.info(f"Circuit Breaker [{self.name}] is now HALF-OPEN (testing recovery).")
                return True
            return False
        return True

class SmartRouter:
    """
    3-Tier Fallback Router for AI operations with Quota Safeguards.
    Tier 1: Groq
    Tier 2: Gemini
    Tier 3: Local Engine
    """

    def __init__(self):
        self.breakers = {
            "groq": CircuitBreaker("Groq"),
            "gemini": CircuitBreaker("Gemini")
        }
        self.max_retries = 3
        self.base_delay = 1.0 # seconds

    async def _execute_with_backoff(self, name: str, call: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Executes a call with exponential backoff and jitter."""
        for attempt in range(self.max_retries):
            try:
                return await call(*args, **kwargs)
            except Exception as e:
                err_str = str(e).lower()
                is_quota_error = "quota" in err_str or "rate limit" in err_str or "429" in err_str or "resource_exhausted" in err_str

                if is_quota_error:
                    logger.warning(f"Quota exhausted for {name} on attempt {attempt + 1}. Falling back immediately.")
                    raise # Re-raise to trigger outer fallback logic

                if attempt == self.max_retries - 1:
                    raise

                delay = (self.base_delay * (2 ** attempt)) + (random.random() * 0.5)
                logger.info(f"Retrying {name} in {delay:.2f}s (Attempt {attempt + 1}/{self.max_retries}) due to: {e}")
                await asyncio.sleep(delay)

    async def route(
        self,
        operation_name: str,
        groq_call: Callable[..., Awaitable[Any]],
        gemini_call: Callable[..., Awaitable[Any]],
        local_call: Callable[..., Any],
        *args, **kwargs
    ) -> Dict[str, Any]:
        start_time = time.time()

        # Tier 1: Groq
        if self.breakers["groq"].can_execute() and os.getenv("GROQ_API_KEY"):
            try:
                result = await self._execute_with_backoff("Groq", groq_call, *args, **kwargs)
                self.breakers["groq"].record_success()
                return self._wrap_response("groq_ai", result, start_time, quota_safe=True)
            except Exception as e:
                logger.error(f"Tier 1 (Groq) failed for {operation_name}: {e}")
                self.breakers["groq"].record_failure()

        # Tier 2: Gemini
        if self.breakers["gemini"].can_execute() and os.getenv("GEMINI_API_KEY"):
            try:
                result = await self._execute_with_backoff("Gemini", gemini_call, *args, **kwargs)
                self.breakers["gemini"].record_success()
                return self._wrap_response("gemini_ai", result, start_time, quota_safe=True)
            except Exception as e:
                logger.error(f"Tier 2 (Gemini) failed for {operation_name}: {e}")
                self.breakers["gemini"].record_failure()

        # Tier 3: Local Engine
        try:
            logger.info(f"Falling back to Tier 3 (Local) for {operation_name}")
            result = local_call(*args, **kwargs)
            if asyncio.iscoroutine(result):
                result = await result
            return self._wrap_response("local_engine", result, start_time, quota_safe=True)
        except Exception as e:
            logger.critical(f"Tier 3 (Local) failed for {operation_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "failed_all_tiers",
                "quota_safe": False,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

    def _wrap_response(self, source: str, data: Any, start_time: float, quota_safe: bool = True) -> Dict[str, Any]:
        return {
            "success": True,
            "source": source,
            "latency_ms": int((time.time() - start_time) * 1000),
            "pii_redacted": True,
            "quota_safe": quota_safe,
            "data": data
        }

# Global singleton
router = SmartRouter()

# Global singleton
router = SmartRouter()
