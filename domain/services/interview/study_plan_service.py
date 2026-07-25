from typing import List, Set

from domain.shared.value_objects import CandidateId, StudyPlanId
from domain.tracking.interview_entities import StudyPlan, StudyTopic


class StudyPlanService:
    """
    Pure logic for mapping skill gaps and weak areas to a structured learning path.
    """

    @staticmethod
    def generate_plan(
        candidate_id: CandidateId,
        missing_skills: List[str],
        weak_areas: List[str],
        job_id: Optional[str] = None,
    ) -> StudyPlan:
        topics = []

        # 1. Technical topics based on skill gaps
        for skill in missing_skills:
            topics.append(
                StudyTopic(
                    topic=f"Advanced {skill} concepts",
                    priority="high",
                    estimated_time_minutes=120,
                    learning_objectives=[
                        f"Master {skill} syntax",
                        f"Understand {skill} in production",
                    ],
                )
            )

        # 2. General topics based on weak areas
        for area in weak_areas:
            topics.append(
                StudyTopic(
                    topic=area,
                    priority="medium",
                    estimated_time_minutes=60,
                    learning_objectives=[f"Improve confidence in {area}"],
                )
            )

        return StudyPlan(
            id=StudyPlanId(), candidate_id=candidate_id, job_id=job_id, topics=topics
        )
