import logging

from application.dto.output.interview_intelligence_output import \
    InterviewPreparationDTO
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.interview.preparation_service import \
    InterviewPreparationService
from domain.shared.value_objects import CandidateId, JobId

logger = logging.getLogger(__name__)


class GeneratePreparationPlanUseCase(
    ApplicationUseCase[tuple, InterviewPreparationDTO]
):
    def __init__(self, candidate_repo: ICandidateRepository, job_repo: IJobRepository):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo

    async def _run(self, input_data: tuple) -> Result[InterviewPreparationDTO]:
        candidate_id_str, job_id_str = input_data

        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(candidate_id_str)
        )
        job = await self._job_repo.get_by_id(JobId.from_str(job_id_str))

        if not candidate or not job:
            return Result.not_found("Entity not found.")

        strategy = InterviewPreparationService.create_strategy(candidate, job)

        output = InterviewPreparationDTO(
            focus_themes=strategy["focus_themes"],
            estimated_prep_hours=strategy["estimated_prep_hours"],
            recommended_focus=strategy["recommended_focus"],
        )

        return Result.ok(output)

    async def execute(
        self, candidate_id: str, job_id: str
    ) -> Result[InterviewPreparationDTO]:
        return await self._run((candidate_id, job_id))
