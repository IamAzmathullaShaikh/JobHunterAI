from typing import List

from application.dto.input.job_input import JobSearchInputDTO
from application.dto.output.job_output import JobOutputDTO
from application.results.result import Result
from application.use_cases.jobs.recommend_jobs import RecommendJobsUseCase
from application.use_cases.jobs.search_jobs import SearchJobsUseCase


class JobApplicationService:
    """Orchestrates job-related workflows."""

    def __init__(
        self, search_uc: SearchJobsUseCase, recommend_uc: RecommendJobsUseCase
    ):
        self._search_uc = search_uc
        self._recommend_uc = recommend_uc

    async def discovery(self, dto: JobSearchInputDTO) -> Result[List[JobOutputDTO]]:
        return await self._search_uc.execute(dto)

    async def get_recommendations(
        self, candidate_id: str
    ) -> Result[List[JobOutputDTO]]:
        return await self._recommend_uc.execute(candidate_id)
