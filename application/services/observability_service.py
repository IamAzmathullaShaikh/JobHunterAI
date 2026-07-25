import logging
import time
from typing import Any, Dict, Optional

from core.providers.telemetry_dispatcher import dispatcher
from core.providers.telemetry_events import BaseTelemetryEvent

logger = logging.getLogger(__name__)


class ObservabilityService:
    """
    Extends platform telemetry with application-level business metrics.
    """

    def __init__(self):
        self._dispatcher = dispatcher

    def track_business_metric(self, metric_name: str, value: Any, candidate_id: str):
        """Publishes a non-operational metric (e.g. conversion rate)."""
        logger.info(
            f"BUSINESS METRIC | candidate={candidate_id} | {metric_name}={value}"
        )
        # Future: publish a custom BusinessMetricEvent to the dispatcher

    def record_use_case_execution(self, name: str, duration_ms: float, success: bool):
        """Tracking performance of specific application use cases."""
        level = logging.INFO if success else logging.ERROR
        logger.log(
            level,
            f"USE CASE | name={name} | duration={duration_ms:.2f}ms | success={success}",
        )

    def generate_correlation_id(self) -> str:
        import uuid

        return str(uuid.uuid4())[:8]
