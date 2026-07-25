from core.exceptions import JobHunterException


class CircuitBreakerError(JobHunterException):
    """Base exception for circuit breaker related issues."""

    pass


class CallRejectedError(CircuitBreakerError):
    """Raised when a call is blocked because the circuit is currently OPEN."""

    def __init__(self, provider_id: str, state: str):
        super().__init__(
            message=f"Call to '{provider_id}' rejected: Circuit is {state.upper()}.",
            status_code=503,  # Service Unavailable
            details={"provider_id": provider_id, "circuit_state": state},
        )
