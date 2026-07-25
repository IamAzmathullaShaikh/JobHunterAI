from typing import List

from domain.discovery.entities import GapAnalysis, Job, Recommendation
from domain.profile.candidate import Candidate
from domain.services.matching.keyword_coverage import KeywordCoverageService
from domain.services.matching.skill_matching import SkillMatchingService


class GapAnalysisService:
    """
    Generates structured reports on missing requirements and weak areas.
    """

    @staticmethod
    def generate(candidate: Candidate, job: Job) -> GapAnalysis:
        _, _, missing_skills = SkillMatchingService.calculate_score(candidate, job)
        _, missing_keywords = KeywordCoverageService.calculate_score(candidate, job)

        weak_areas = []
        recommendations = []

        if missing_skills:
            weak_areas.append("Technical Skills")
            recommendations.append(
                Recommendation(
                    "skills",
                    f"Missing key skills: {', '.join(missing_skills[:3])}",
                    "high",
                )
            )

        if candidate.total_years_experience < 3.0:  # Arbitrary threshold
            weak_areas.append("Experience Depth")

        return GapAnalysis(
            job_id=job.id,
            candidate_id=candidate.id,
            missing_skills=missing_skills,
            missing_keywords=missing_keywords,
            weak_areas=weak_areas,
            recommendations=recommendations,
        )
