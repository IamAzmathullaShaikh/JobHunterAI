from domain.discovery.entities import Job
from domain.profile.candidate import Candidate


class ExperienceMatchingService:
    """
    Pure logic for validating years of experience and seniority.
    """

    @staticmethod
    def calculate_score(candidate: Candidate, job: Job) -> float:
        candidate_years = candidate.total_years_experience

        # Heuristic mapping for ExperienceLevel to years if not explicitly provided
        # In a real app, this would be in configuration or JobRequirement
        level_requirements = {
            "entry": 0,
            "junior": 1,
            "mid": 3,
            "senior": 5,
            "lead": 8,
            "principal": 10,
        }

        required_years = 0.0
        if job.experience_level:
            required_years = float(
                level_requirements.get(job.experience_level.value.lower(), 0)
            )

        if required_years == 0:
            return 1.0

        score = candidate_years / required_years
        return min(round(score, 2), 1.0)
