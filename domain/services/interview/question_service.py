from typing import List, Optional

from domain.discovery.entities import Job
from domain.profile.candidate import Candidate
from domain.shared.value_objects import QuestionId
from domain.tracking.interview_entities import InterviewQuestion


class InterviewQuestionService:
    """
    Pure logic for selecting and generating interview questions based on
    the intersection of candidate profile and job requirements.
    """

    @staticmethod
    def select_questions(
        candidate: Candidate, job: Job, count: int = 5
    ) -> List[InterviewQuestion]:
        """
        Deterministic selection of questions based on target skills and seniority.
        """
        questions = []

        # 1. Technical questions based on job required skills
        for skill in job.required_skills[:3]:
            questions.append(
                InterviewQuestion(
                    id=QuestionId(),
                    category="technical",
                    difficulty="intermediate",
                    text=f"Can you explain your experience working with {skill}?",
                    target_skill=skill,
                )
            )

        # 2. Behavioural questions based on seniority
        seniority = (
            job.experience_level.value.lower() if job.experience_level else "mid"
        )
        if seniority in ["senior", "lead", "principal"]:
            questions.append(
                InterviewQuestion(
                    id=QuestionId(),
                    category="behavioural",
                    difficulty="advanced",
                    text="Describe a time when you had to lead a difficult project under a tight deadline.",
                )
            )
        else:
            questions.append(
                InterviewQuestion(
                    id=QuestionId(),
                    category="behavioural",
                    difficulty="beginner",
                    text="Tell me about a time you worked in a team to solve a technical problem.",
                )
            )

        # 3. HR / Culture fit
        questions.append(
            InterviewQuestion(
                id=QuestionId(),
                category="hr",
                difficulty="beginner",
                text=f"Why do you want to work at {job.company_id}?",
            )
        )

        return questions[:count]
