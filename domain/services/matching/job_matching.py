from typing import Dict, Optional, Type

from core.config.settings import settings
from domain.discovery.entities import Job, MatchResult
from domain.profile.candidate import Candidate
from domain.services.matching.strategy import (IMatchingStrategy,
                                               WeightedLinearStrategy)


class JobMatchingService:
    """
    Entry point for job matching. Uses swappable strategies and
    injects configuration metadata for reproducibility.
    """

    def __init__(self, strategy: Optional[IMatchingStrategy] = None):
        self._strategy = strategy or WeightedLinearStrategy()

    def calculate_match(
        self, candidate: Candidate, job: Job, weights: Optional[Dict[str, float]] = None
    ) -> MatchResult:
        # 1. Use configured weights from settings if not provided
        active_weights = weights or settings.MATCHING_WEIGHTS

        # 2. Execute Strategy
        result = self._strategy.calculate(candidate, job, active_weights)

        # 3. Enrich with Versioning Metadata
        # We create a new result object with metadata (since frozen=True)
        # Note: In a real app we might use .replace() or similar
        from dataclasses import replace

        return replace(
            result,
            configuration_version=settings.MATCHING_CONFIG_VERSION,
            matching_strategy=self._strategy.__class__.__name__.lower(),
            weights_version="settings_default" if not weights else "runtime_override",
        )
