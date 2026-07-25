from typing import List, Set, Tuple

from core.config.settings import settings
from domain.discovery.entities import Job
from domain.profile.candidate import Candidate


class SkillMatchingService:
    """
    Pure logic for calculating skill overlap between a candidate and a job.
    Includes deterministic alias resolution.
    """

    @staticmethod
    def _normalize_skill(skill: str) -> str:
        """Resolves aliases and normalizes strings."""
        s = skill.lower().strip()
        return settings.SKILL_ALIASES.get(s, s)

    @staticmethod
    def calculate_score(
        candidate: Candidate, job: Job
    ) -> Tuple[float, List[str], List[str]]:
        """
        Returns (score, matched_skills, missing_skills)
        """
        candidate_skills = {
            SkillMatchingService._normalize_skill(s.name) for s in candidate.skills
        }
        required_skills = {
            SkillMatchingService._normalize_skill(s) for s in job.required_skills
        }
        preferred_skills = {
            SkillMatchingService._normalize_skill(s) for s in job.preferred_skills
        }

        if not required_skills and not preferred_skills:
            return 1.0, [], []

        matched_required = candidate_skills.intersection(required_skills)
        missing_required = required_skills.difference(candidate_skills)

        matched_preferred = candidate_skills.intersection(preferred_skills)

        # Weighted score: required skills count more
        required_weight = 0.8
        preferred_weight = 0.2

        r_score = (
            len(matched_required) / len(required_skills) if required_skills else 1.0
        )
        p_score = (
            len(matched_preferred) / len(preferred_skills) if preferred_skills else 1.0
        )

        final_score = (r_score * required_weight) + (p_score * preferred_weight)

        return (
            round(final_score, 2),
            list(matched_required.union(matched_preferred)),
            list(missing_required),
        )
