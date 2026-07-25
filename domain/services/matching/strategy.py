from abc import ABC, abstractmethod
from typing import Dict, Optional

from domain.discovery.entities import Job, MatchBreakdown, MatchResult
from domain.profile.candidate import Candidate
from domain.services.matching.education_matching import \
    EducationMatchingService
from domain.services.matching.experience_matching import \
    ExperienceMatchingService
from domain.services.matching.keyword_coverage import KeywordCoverageService
from domain.services.matching.skill_matching import SkillMatchingService


class IMatchingStrategy(ABC):
    """
    Interface for different job matching algorithms.
    """

    @abstractmethod
    def calculate(
        self, candidate: Candidate, job: Job, weights: Dict[str, float]
    ) -> MatchResult:
        pass


class WeightedLinearStrategy(IMatchingStrategy):
    """
    Default strategy using a weighted linear combination of scores.
    """

    def calculate(
        self, candidate: Candidate, job: Job, weights: Dict[str, float]
    ) -> MatchResult:
        skill_score, matched_skills, missing_skills = (
            SkillMatchingService.calculate_score(candidate, job)
        )
        exp_score = ExperienceMatchingService.calculate_score(candidate, job)
        edu_score = EducationMatchingService.calculate_score(candidate, job)
        kw_score, _ = KeywordCoverageService.calculate_score(candidate, job)

        # Heuristics for location/salary
        loc_score = 1.0 if job.location.is_remote else 0.0
        sal_score = 1.0 if job.salary_range else 0.5

        breakdown = MatchBreakdown(
            skills_score=skill_score,
            experience_score=exp_score,
            education_score=edu_score,
            keywords_score=kw_score,
            location_score=loc_score,
            salary_score=sal_score,
        )

        overall = (
            (skill_score * weights.get("skills", 0))
            + (exp_score * weights.get("experience", 0))
            + (edu_score * weights.get("education", 0))
            + (kw_score * weights.get("keywords", 0))
            + (loc_score * weights.get("location", 0))
            + (sal_score * weights.get("salary", 0))
        )

        return MatchResult(
            job_id=job.id,
            candidate_id=candidate.id,
            overall_score=round(overall, 2),
            breakdown=breakdown,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            fit_summary=f"Weighted match score: {round(overall * 100)}%",
        )


class SkillFirstStrategy(WeightedLinearStrategy):
    """Overrides weights to prioritize skills."""

    def calculate(
        self, candidate: Candidate, job: Job, weights: Dict[str, float]
    ) -> MatchResult:
        custom_weights = weights.copy()
        custom_weights["skills"] = 0.6
        # Distribute remaining 0.4 proportionately or set fixed
        return super().calculate(candidate, job, custom_weights)


class ExperienceFirstStrategy(WeightedLinearStrategy):
    """Overrides weights to prioritize experience."""

    def calculate(
        self, candidate: Candidate, job: Job, weights: Dict[str, float]
    ) -> MatchResult:
        custom_weights = weights.copy()
        custom_weights["experience"] = 0.6
        return super().calculate(candidate, job, custom_weights)
