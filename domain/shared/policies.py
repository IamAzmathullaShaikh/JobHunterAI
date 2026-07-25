from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class RetryPolicy:
    """Strategy for re-attempting failed operations."""

    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    backoff_factor: float = 2.0
    jitter: bool = True


@dataclass(frozen=True)
class TimeoutPolicy:
    """Deadlines for execution of various stages."""

    total_timeout_seconds: float = 60.0
    provider_timeout_seconds: float = 30.0
    db_timeout_seconds: float = 10.0


@dataclass(frozen=True)
class FallbackPolicy:
    """Rules for switching to alternative providers or logic."""

    switch_after_failures: int = 2
    recovery_cooldown_seconds: int = 300
    allow_deterministic_fallback: bool = True
