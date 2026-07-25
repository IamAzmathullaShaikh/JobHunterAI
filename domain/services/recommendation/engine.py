from typing import Dict, List, Optional

from domain.profile.candidate import Candidate
from domain.shared.analytics_models import KPI, Recommendation
from domain.shared.enums import SkillCategory


class RecommendationEngineService:
    """
    Deterministic engine for generating prioritized career tasks.
    """

    @staticmethod
    def generate_recommendations(
        candidate: Candidate, kpis: List[KPI]
    ) -> List[Recommendation]:
        recommendations = []

        # 1. KPI-Based Recommendations
        for kpi in kpis:
            if kpi.id == "resume_quality" and kpi.current_value < 0.7:
                recommendations.append(
                    Recommendation(
                        id="rec_res_qual",
                        category="resume",
                        priority="high",
                        message="Improve your base resume score.",
                        reason="Low completeness and formatting detected.",
                        evidence=f"Current score {kpi.current_value} is below threshold 0.7",
                        expected_impact=0.3,
                    )
                )

            if kpi.id == "avg_match" and kpi.current_value < 0.5:
                recommendations.append(
                    Recommendation(
                        id="rec_match_avg",
                        category="matching",
                        priority="critical",
                        message="Acquire more technical skills in your target niche.",
                        reason="Low overlap with job requirements in your saved list.",
                        evidence=f"Average match rate is only {kpi.current_value * 100}%",
                        expected_impact=0.5,
                    )
                )

        # 2. Profile-Based Recommendations
        if not any(s.category == SkillCategory.SOFT for s in candidate.skills):
            recommendations.append(
                Recommendation(
                    id="rec_soft_skills",
                    category="skills",
                    priority="medium",
                    message="Add soft skills (Communication, Leadership) to your profile.",
                    reason="Modern ATS and recruiters look for balanced profiles.",
                    evidence="Zero soft skills detected in profile.",
                    expected_impact=0.1,
                )
            )

        return recommendations
