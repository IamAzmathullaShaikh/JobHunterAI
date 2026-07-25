from pydantic import BaseModel, Field


class BreakerPolicy(BaseModel):
    """Configuration policy for circuit breaker behavior."""

    failure_threshold: int = Field(
        5, description="Consecutive failures before opening the circuit."
    )
    recovery_timeout: float = Field(
        60.0, description="Seconds to wait in OPEN state before trying HALF-OPEN."
    )
    success_threshold: int = Field(
        2, description="Consecutive successes needed in HALF-OPEN to close the circuit."
    )
    minimum_requests: int = Field(
        0, description="Minimum requests before the breaker is allowed to open."
    )

    # Classification settings
    track_429: bool = True
    track_5xx: bool = True
    track_timeouts: bool = True
