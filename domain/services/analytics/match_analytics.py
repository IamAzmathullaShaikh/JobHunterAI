from typing import List

from domain.discovery.entities import MatchResult
from domain.shared.analytics_models import KPI, Trend, TrendDirection


class MatchAnalyticsService:
    """
    Pure logic for calculating job match metrics and distribution.
    """

    @staticmethod
    def calculate_average_match_kpi(match_history: List[MatchResult]) -> KPI:
        if not match_history:
            return KPI(id="avg_match", name="Average Match Score", current_value=0.0)

        scores = [m.overall_score for m in match_history]
        avg = sum(scores) / len(scores)

        # Calculate trend vs first half of history
        trend = None
        if len(scores) >= 4:
            mid = len(scores) // 2
            prev_avg = sum(scores[:mid]) / mid
            curr_avg = sum(scores[mid:]) / (len(scores) - mid)

            delta = ((curr_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0.0
            direction = (
                TrendDirection.UP
                if delta > 0
                else (TrendDirection.DOWN if delta < 0 else TrendDirection.STABLE)
            )

            trend = Trend(
                direction=direction,
                delta_percentage=round(abs(delta), 1),
                previous_value=round(prev_avg, 2),
                current_value=round(curr_avg, 2),
            )

        return KPI(
            id="avg_match",
            name="Average Match Score",
            current_value=round(avg, 2),
            target_value=0.8,
            trend=trend,
        )
