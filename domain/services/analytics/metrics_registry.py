from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from domain.shared.analytics_models import KPI


@dataclass(frozen=True)
class MetricMetadata:
    id: str
    name: str
    unit: str  # percentage, count, days, usd
    category: str  # resume, matching, application, interview, career
    aggregation_strategy: str  # latest, average, sum, min, max
    refresh_policy: str  # real-time, daily, on-demand
    description: str
    is_active: bool = True


class MetricsRegistry:
    """
    Central registry for all system-defined KPIs and metrics.
    Decouples metric definitions from calculation logic.
    """

    def __init__(self):
        self._metrics: Dict[str, MetricMetadata] = {
            "resume_quality": MetricMetadata(
                id="resume_quality",
                name="Resume Quality Score",
                unit="percentage",
                category="resume",
                aggregation_strategy="latest",
                refresh_policy="on-demand",
                description="Overall quality of the latest resume version.",
            ),
            "avg_match_score": MetricMetadata(
                id="avg_match",
                name="Average Match Score",
                unit="percentage",
                category="matching",
                aggregation_strategy="average",
                refresh_policy="on-demand",
                description="Mean fit score across all identified jobs.",
            ),
            "pipeline_velocity": MetricMetadata(
                id="pipeline_velocity",
                name="Pipeline Velocity",
                unit="days",
                category="application",
                aggregation_strategy="average",
                refresh_policy="daily",
                description="Average number of days an application stays in one stage.",
            ),
            "conversion_rate": MetricMetadata(
                id="conversion_rate",
                name="Interview Conversion Rate",
                unit="percentage",
                category="application",
                aggregation_strategy="latest",
                refresh_policy="on-demand",
                description="Percentage of applications that reach the interview stage.",
            ),
        }

    def get_metric(self, metric_id: str) -> Optional[MetricMetadata]:
        return self._metrics.get(metric_id)

    def list_by_category(self, category: str) -> List[MetricMetadata]:
        return [m for m in self._metrics.values() if m.category == category]

    def list_all(self) -> List[MetricMetadata]:
        return list(self._metrics.values())
