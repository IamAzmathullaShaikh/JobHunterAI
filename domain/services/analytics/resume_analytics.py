from typing import Dict, List

from domain.profile.candidate import Candidate
from domain.profile.entities import Resume
from domain.services.analysis import ResumeScoringService
from domain.shared.analytics_models import (KPI, TimeSeriesMetric, Trend,
                                            TrendDirection)


class ResumeAnalyticsService:
    """
    Pure logic for calculating resume-related metrics and trends.
    """

    @staticmethod
    def calculate_quality_kpi(
        resume: Resume, candidate: Candidate, previous_versions: List[Resume] = None
    ) -> KPI:
        current_scores = ResumeScoringService.calculate_score(resume, candidate)
        current_val = current_scores["overall_score"]

        trend = None
        if previous_versions:
            # Simple comparison with the last version
            last_version = previous_versions[-1]
            # Note: This is heuristic since we don't have historical candidate state here
            prev_val = last_version.calculate_completeness()  # Simplified

            delta = ((current_val - prev_val) / prev_val * 100) if prev_val > 0 else 0.0
            direction = (
                TrendDirection.UP
                if delta > 0
                else (TrendDirection.DOWN if delta < 0 else TrendDirection.STABLE)
            )

            trend = Trend(
                direction=direction,
                delta_percentage=round(abs(delta), 1),
                previous_value=prev_val,
                current_value=current_val,
            )

        return KPI(
            id="resume_quality",
            name="Resume Quality Score",
            current_value=current_val,
            target_value=0.9,
            trend=trend,
        )
