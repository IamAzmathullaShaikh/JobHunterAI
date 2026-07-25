from typing import List, Tuple

from domain.discovery.entities import Job
from domain.profile.candidate import Candidate


class KeywordCoverageService:
    """
    Analyzes presence of industry-specific terms in the resume vs job description.
    """

    @staticmethod
    def calculate_score(candidate: Candidate, job: Job) -> Tuple[float, List[str]]:
        """
        Returns (score, missing_keywords)
        """
        # In a real implementation, we might use an IKeywordExtractorProvider
        # to get keywords from the job description raw text.
        # For the domain service, we'll assume keywords are already identified or
        # use a simple word-frequency/intersection if needed.

        # Heuristic: use required_skills as keywords if none provided
        keywords = set(job.required_skills)
        if not keywords:
            return 1.0, []

        resume_text = ""
        # Assuming Candidate has a way to get all resume texts, but for now
        # let's assume we are checking the latest resume.
        resume = candidate.latest_resume()
        if not resume:
            return 0.0, list(keywords)

        found = []
        missing = []
        for kw in keywords:
            if resume.contains_keyword(kw):
                found.append(kw)
            else:
                missing.append(kw)

        score = len(found) / len(keywords)
        return round(score, 2), missing
