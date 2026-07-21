import time
import asyncio
import os
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
    3-Tier Fallback Router for AI operations.
    Tier 1: Groq
    Tier 2: Gemini
    Tier 3: Local Engine
    """

    def __init__(self):
        self.breakers = {
            "groq": CircuitBreaker("Groq"),
            "gemini": CircuitBreaker("Gemini")
        }

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
                result = await groq_call(*args, **kwargs)
                self.breakers["groq"].record_success()
                return self._wrap_response("groq_ai", result, start_time)
            except Exception as e:
                logger.error(f"Tier 1 (Groq) failed for {operation_name}: {e}")
                self.breakers["groq"].record_failure()

        # Tier 2: Gemini
        if self.breakers["gemini"].can_execute() and os.getenv("GEMINI_API_KEY"):
            try:
                result = await gemini_call(*args, **kwargs)
                self.breakers["gemini"].record_success()
                return self._wrap_response("gemini_ai", result, start_time)
            except Exception as e:
                logger.error(f"Tier 2 (Gemini) failed for {operation_name}: {e}")
                self.breakers["gemini"].record_failure()

        # Tier 3: Local Engine
        try:
            logger.info(f"Falling back to Tier 3 (Local) for {operation_name}")
            result = local_call(*args, **kwargs)
            # If local_call is async (unlikely based on requirement but for safety)
            if asyncio.iscoroutine(result):
                result = await result
            return self._wrap_response("local_engine", result, start_time)
        except Exception as e:
            logger.critical(f"Tier 3 (Local) failed for {operation_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "failed_all_tiers",
                "latency_ms": int((time.time() - start_time) * 1000)
            }

    def _wrap_response(self, source: str, data: Any, start_time: float) -> Dict[str, Any]:
        return {
            "success": True,
            "source": source,
            "latency_ms": int((time.time() - start_time) * 1000),
            "pii_redacted": True, # Privacy redactor is handled before routing
            "data": data
        }

# Global singleton
router = SmartRouter()
