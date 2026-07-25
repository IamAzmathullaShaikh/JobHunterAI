from typing import Dict, List, Optional

from domain.discovery.entities import ATSScore, MatchResult
from domain.shared.value_objects import ReadinessScore


class InterviewReadinessService:
    """
    Pure logic for aggregating various data points into a final interview readiness report.
    """

    @staticmethod
    def calculate_readiness(
        match_result: MatchResult,
        ats_score: ATSScore,
        mock_sessions_count: int,
        average_mock_score: float,
    ) -> ReadinessScore:
        category_scores = {
            "job_alignment": match_result.overall_score,
            "resume_quality": ats_score.overall_score,
            "practice_effort": min(mock_sessions_count / 3.0, 1.0),
            "practice_quality": average_mock_score,
        }

        overall = sum(category_scores.values()) / len(category_scores)

        priorities = []
        if match_result.overall_score < 0.7:
            priorities.append("Bridge technical skill gaps identified in matching.")
        if ats_score.overall_score < 0.8:
            priorities.append("Improve resume formatting and quantification.")
        if mock_sessions_count < 2:
            priorities.append(
                "Schedule more mock interview sessions to improve confidence."
            )

        return ReadinessScore(
            overall_score=round(overall, 2),
            category_scores=category_scores,
            improvement_priorities=priorities,
            is_ready=overall > 0.75,
        )
