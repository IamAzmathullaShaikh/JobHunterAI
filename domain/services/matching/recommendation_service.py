from typing import List

from domain.discovery.entities import GapAnalysis, Job, Recommendation
from domain.profile.candidate import Candidate


class RecommendationService:
    """
    Produces actionable advice based on gap analysis.
    """

    @staticmethod
    def get_recommendations(gap_analysis: GapAnalysis) -> List[Recommendation]:
        # Orchestrate and refine recommendations
        # This could involve merging with AI-generated suggestions later
        return gap_analysis.recommendations
