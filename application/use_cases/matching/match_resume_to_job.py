from application.dto.input.job_input import CalculateMatchInputDTO
from application.dto.output.matching_output import JobMatchDTO
from application.mappers.job_mapper import JobMapper
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from core.config.settings import settings
from domain.services.matching.job_matching import JobMatchingService
from domain.shared.value_objects import CandidateId, JobId


class MatchResumeToJobUseCase(ApplicationUseCase[CalculateMatchInputDTO, JobMatchDTO]):
    """
    Standard use case for calculating a match between a candidate and a specific job.
    """

    def __init__(self, candidate_repo: ICandidateRepository, job_repo: IJobRepository):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo

    async def _run(self, input_dto: CalculateMatchInputDTO) -> Result[JobMatchDTO]:
        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(input_dto.candidate_id)
        )
        job = await self._job_repo.get_by_id(JobId.from_str(input_dto.job_id))

        if not candidate:
            return Result.not_found("Candidate not found.")
        if not job:
            return Result.not_found("Job not found.")

        # Configuration-driven weights
        weights = getattr(settings, "MATCHING_WEIGHTS", None)

        match = JobMatchingService.calculate_match(candidate, job, weights=weights)

        return Result.ok(JobMapper.to_match_result_dto(match))
