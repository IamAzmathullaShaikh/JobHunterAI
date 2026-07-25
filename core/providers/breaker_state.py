from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CircuitState(str, Enum):
    """The three possible states of a circuit breaker."""

    CLOSED = "closed"  # Healthy, requests flow normally
    OPEN = "open"  # Failing, requests blocked immediately
    HALF_OPEN = "half_open"  # Recovery testing, limited requests allowed


class ProviderBreakerState(BaseModel):
    """Runtime state tracking for a single provider's circuit."""

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None

    def reset(self):
        """Returns the state to healthy defaults."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_at = None
        self.opened_at = None
