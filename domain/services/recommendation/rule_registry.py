from dataclasses import dataclass, field
from typing import Dict, List, Optional

from domain.shared.analytics_models import Recommendation


@dataclass(frozen=True)
class RecommendationRule:
    """Metadata and versioning for a deterministic recommendation rule."""

    id: str
    version: str
    category: str
    priority: str  # critical, high, medium, low
    trigger_metric: str  # ID of the KPI that triggers this rule
    threshold: float
    message_template: str
    is_enabled: bool = True


class RecommendationRegistry:
    """
    Central authority for managing recommendation rules and their metadata.
    """

    def __init__(self):
        self._rules: Dict[str, RecommendationRule] = {
            "rec_res_qual": RecommendationRule(
                id="rec_res_qual",
                version="1.0.0",
                category="resume",
                priority="high",
                trigger_metric="resume_quality",
                threshold=0.7,
                message_template="Your resume score is {{ value }}. Focus on quantifying achievements.",
            ),
            "rec_match_avg": RecommendationRule(
                id="rec_match_avg",
                version="1.0.0",
                category="matching",
                priority="critical",
                trigger_metric="avg_match",
                threshold=0.5,
                message_template="Average match rate is low ({{ value }}). Consider upskilling.",
            ),
            "rec_velocity": RecommendationRule(
                id="rec_velocity",
                version="1.1.0",
                category="application",
                priority="medium",
                trigger_metric="pipeline_velocity",
                threshold=7.0,  # 7 days
                message_template="Applications are stagnant. Follow up with recruiters.",
            ),
        }

    def get_rule(self, rule_id: str) -> Optional[RecommendationRule]:
        return self._rules.get(rule_id)

    def list_active_rules(self) -> List[RecommendationRule]:
        return [r for r in self._rules.values() if r.is_enabled]
