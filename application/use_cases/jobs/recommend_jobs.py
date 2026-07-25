from typing import List

from application.dto.output.job_output import JobOutputDTO
from application.mappers.job_mapper import JobMapper
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.matching.job_matching import JobMatchingService
from domain.shared.value_objects import CandidateId


class RecommendJobsUseCase(ApplicationUseCase[str, List[JobOutputDTO]]):
    def __init__(self, candidate_repo: ICandidateRepository, job_repo: IJobRepository):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo

    async def _run(self, candidate_id: str) -> Result[List[JobOutputDTO]]:
        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(candidate_id)
        )
        if not candidate:
            return Result.not_found("Candidate not found.")

        all_jobs = await self._job_repo.list_active(limit=100)

        recommendations = []
        for job in all_jobs:
            match = JobMatchingService.calculate_fit(candidate, job)
            if match.score > 0.5:
                recommendations.append(JobMapper.to_output_dto(job))

        return Result.ok(recommendations)

    async def execute(self, candidate_id: str) -> Result[List[JobOutputDTO]]:
        return await self._run(candidate_id)
