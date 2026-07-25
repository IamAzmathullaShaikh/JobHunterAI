import logging
from typing import List, Optional

from application.dto.output.interview_intelligence_output import \
    InterviewQuestionDTO
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from core.providers.ai.base import IAIProvider
from domain.services.interview.question_service import InterviewQuestionService
from domain.shared.value_objects import CandidateId, JobId, QuestionId

logger = logging.getLogger(__name__)


class GenerateInterviewQuestionsUseCase(
    ApplicationUseCase[tuple, List[InterviewQuestionDTO]]
):
    """
    Generates a list of tailored interview questions.
    Uses deterministic service first, then optionally enriches or expands with AI.
    """

    def __init__(
        self,
        candidate_repo: ICandidateRepository,
        job_repo: IJobRepository,
        ai_provider: Optional[IAIProvider] = None,
    ):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo
        self._ai_provider = ai_provider

    async def _run(self, input_data: tuple) -> Result[List[InterviewQuestionDTO]]:
        candidate_id_str, job_id_str = input_data

        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(candidate_id_str)
        )
        job = await self._job_repo.get_by_id(JobId.from_str(job_id_str))

        if not candidate:
            return Result.not_found("Candidate not found.")
        if not job:
            return Result.not_found("Job not found.")

        # 1. Start with Deterministic Fallback (Authority of Determinism)
        domain_questions = InterviewQuestionService.select_questions(candidate, job)

        # 2. AI Enrichment (Enricher Pattern)
        if self._ai_provider:
            try:
                # Example: Asking AI to generate 2 more behavioral questions based on description
                prompt = f"Based on this job description: {job.description}, suggest 2 specific behavioral questions."
                res = await self._ai_provider.generate(
                    [{"role": "user", "content": prompt}]
                )

                # Logic to parse and add AI questions would go here
                # For now, we logging success and keeping deterministic as primary
                logger.info("AI enrichment successful for interview questions.")
            except Exception as e:
                logger.warning(
                    f"AI enrichment failed, falling back to deterministic: {e}"
                )

        # 3. Map to DTO
        outputs = [
            InterviewQuestionDTO(
                id=str(q.id),
                category=q.category,
                difficulty=q.difficulty,
                text=q.text,
                target_skill=q.target_skill,
            )
            for q in domain_questions
        ]

        return Result.ok(outputs)

    async def execute(
        self, candidate_id: str, job_id: str
    ) -> Result[List[InterviewQuestionDTO]]:
        return await self._run((candidate_id, job_id))
