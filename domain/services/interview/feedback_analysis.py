from typing import Dict, List

from domain.tracking.interview_entities import InterviewSession


class FeedbackAnalysisService:
    """
    Pure logic for aggregating feedback from an interview session.
    """

    @staticmethod
    def analyze_session(session: InterviewSession) -> Dict[str, any]:
        if not session.answers:
            return {"status": "no_data", "summary": "No answers recorded."}

        avg_score = sum(
            a.star_analysis.completeness_score
            for a in session.answers
            if a.star_analysis
        ) / len(session.answers)

        # Identifying consistent weak spots in STAR
        missing_components = []
        if any(
            not a.star_analysis.has_result for a in session.answers if a.star_analysis
        ):
            missing_components.append("Results and metrics")
        if any(
            not a.star_analysis.has_action for a in session.answers if a.star_analysis
        ):
            missing_components.append("Specific actions taken")

        return {
            "average_star_score": round(avg_score, 2),
            "critical_gaps": missing_components,
            "overall_sentiment": "Positive" if avg_score > 0.7 else "Needs Improvement",
        }
