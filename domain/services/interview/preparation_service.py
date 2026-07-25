from typing import Dict, List

from domain.discovery.entities import Job
from domain.profile.candidate import Candidate


class InterviewPreparationService:
    """
    Pure logic for creating a high-level preparation strategy.
    """

    @staticmethod
    def create_strategy(candidate: Candidate, job: Job) -> Dict[str, any]:
        # Logic to identify 'Themes' for the interview
        themes = ["Technical Mastery"]
        if "senior" in job.title.lower() or (
            job.experience_level and job.experience_level.value.lower() == "senior"
        ):
            themes.append("Leadership & Scale")

        if job.work_mode and job.work_mode.value.lower() == "remote":
            themes.append("Remote Communication")

        return {
            "focus_themes": themes,
            "estimated_prep_hours": 4 + (2 * len(job.required_skills)),
            "recommended_focus": "Mastering the STAR method for technical examples.",
        }
