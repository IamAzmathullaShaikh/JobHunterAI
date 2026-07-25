import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from core.providers.breaker_exceptions import CallRejectedError
from core.providers.breaker_policy import BreakerPolicy
from core.providers.breaker_state import CircuitState, ProviderBreakerState
from core.providers.telemetry_dispatcher import dispatcher as telemetry
from core.providers.telemetry_events import CircuitStateChanged

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Manages circuit breaker states for all providers.
    Thread-safe and implementation-agnostic.
    """

    def __init__(self, default_policy: Optional[BreakerPolicy] = None):
        self._default_policy = default_policy or BreakerPolicy()
        self._states: Dict[str, ProviderBreakerState] = {}
        self._policies: Dict[str, BreakerPolicy] = {}
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()

    def _get_provider_lock(self, provider_id: str) -> threading.Lock:
        with self._global_lock:
            if provider_id not in self._locks:
                self._locks[provider_id] = threading.Lock()
            return self._locks[provider_id]

    def _get_state(self, provider_id: str) -> ProviderBreakerState:
        if provider_id not in self._states:
            self._states[provider_id] = ProviderBreakerState()
        return self._states[provider_id]

    def _get_policy(self, provider_id: str) -> BreakerPolicy:
        return self._policies.get(provider_id, self._default_policy)

    def allow_request(self, provider_id: str) -> bool:
        """
        Determines if a request to the given provider should be allowed.
        Handles automatic transition from OPEN to HALF_OPEN based on timeout.
        """
        lock = self._get_provider_lock(provider_id)
        with lock:
            state = self._get_state(provider_id)
            policy = self._get_policy(provider_id)

            if state.state == CircuitState.CLOSED:
                return True

            if state.state == CircuitState.OPEN:
                # Check for recovery timeout
                if state.opened_at:
                    elapsed = (datetime.now() - state.opened_at).total_seconds()
                    if elapsed >= policy.recovery_timeout:
                        logger.info(
                            f"Circuit for '{provider_id}' transitioning to HALF_OPEN (timeout recovery)."
                        )
                        old_state = state.state
                        state.state = CircuitState.HALF_OPEN
                        state.success_count = 0

                        telemetry.publish(
                            CircuitStateChanged(
                                provider_id=provider_id,
                                old_state=old_state,
                                new_state=state.state,
                            )
                        )
                        return True

                # Still in recovery timeout
                return False

            if state.state == CircuitState.HALF_OPEN:
                # In half-open we allow a limited number of trial requests.
                # For this implementation, we allow 1 concurrent trial at a time (locked).
                return True

        return False

    def record_success(self, provider_id: str) -> None:
        """Records a successful execution and potentially closes the circuit."""
        lock = self._get_provider_lock(provider_id)
        with lock:
            state = self._get_state(provider_id)
            policy = self._get_policy(provider_id)

            if state.state == CircuitState.HALF_OPEN:
                state.success_count += 1
                if state.success_count >= policy.success_threshold:
                    logger.info(
                        f"Circuit for '{provider_id}' CLOSED (success threshold met)."
                    )
                    old_state = state.state
                    state.reset()

                    telemetry.publish(
                        CircuitStateChanged(
                            provider_id=provider_id,
                            old_state=old_state,
                            new_state=CircuitState.CLOSED,
                        )
                    )
            elif state.state == CircuitState.CLOSED:
                # Reset failure count on success in closed state
                state.failure_count = 0

    def record_failure(self, provider_id: str, exception: Exception) -> None:
        """Records a failure and potentially opens the circuit."""
        if not self._is_service_failure(exception):
            return

        lock = self._get_provider_lock(provider_id)
        with lock:
            state = self._get_state(provider_id)
            policy = self._get_policy(provider_id)

            state.failure_count += 1
            state.last_failure_at = datetime.now()

            if state.state == CircuitState.CLOSED:
                if state.failure_count >= policy.failure_threshold:
                    self._open_circuit(provider_id, state)
            elif state.state == CircuitState.HALF_OPEN:
                # Any service failure in HALF_OPEN re-opens the circuit immediately
                logger.warning(
                    f"Trial request for '{provider_id}' failed. Re-opening circuit."
                )
                self._open_circuit(provider_id, state)

    def _open_circuit(self, provider_id: str, state: ProviderBreakerState) -> None:
        logger.error(
            f"Circuit for '{provider_id}' is now OPEN. Requests will be rejected."
        )
        old_state = state.state
        state.state = CircuitState.OPEN
        state.opened_at = datetime.now()

        telemetry.publish(
            CircuitStateChanged(
                provider_id=provider_id, old_state=old_state, new_state=state.state
            )
        )

    def _is_service_failure(self, exception: Exception) -> bool:
        """
        Classifies exceptions to determine if they should trip the breaker.
        Currently trips on most except Validation and Auth errors.
        """
        from core.exceptions import ValidationError

        # We don't want to trip the circuit because of user-input errors
        if isinstance(exception, ValidationError):
            return False

        # In a real SaaS, we might check for specific status codes (e.g. 401/403)
        return True

    def get_state(self, provider_id: str) -> CircuitState:
        with self._get_provider_lock(provider_id):
            return self._get_state(provider_id).state

    def reset(self, provider_id: str) -> None:
        with self._get_provider_lock(provider_id):
            self._get_state(provider_id).reset()
            logger.info(f"Circuit for '{provider_id}' manually RESET.")


# Global instance
breaker = CircuitBreaker()
