from domain.discovery.entities import Job
from domain.profile.candidate import Candidate


class EducationMatchingService:
    """
    Pure logic for checking degree requirements using an ordered hierarchy.
    """

    # Ordered from lowest to highest
    HIERARCHY = ["high_school", "diploma", "bachelor", "master", "phd"]

    @staticmethod
    def _get_rank(degree: str) -> int:
        d = degree.lower().replace(" ", "_")
        # Heuristic matching for degree names
        if "phd" in d or "doctorate" in d:
            return 4
        if "master" in d or "msc" in d or "mba" in d:
            return 3
        if "bachelor" in d or "bsc" in d or "ba" in d:
            return 2
        if "diploma" in d:
            return 1
        return 0  # high_school or unknown

    @staticmethod
    def calculate_score(candidate: Candidate, job: Job) -> float:
        # Assuming Job has a 'required_degree' string in a real scenario,
        # for now we'll search required_skills or metadata.
        # Let's assume a default requirement of 'bachelor' if not specified.
        required_degree = "bachelor"  # Placeholder requirement
        target_rank = EducationMatchingService._get_rank(required_degree)

        if not candidate.educations:
            return 0.0

        candidate_ranks = [
            EducationMatchingService._get_rank(edu.degree)
            for edu in candidate.educations
        ]
        max_candidate_rank = max(candidate_ranks)

        if max_candidate_rank >= target_rank:
            return 1.0  # Meets or exceeds

        # Partial credit: ratio of ranks
        return round(max_candidate_rank / target_rank, 2)
