from typing import List

from application.dto.common.location_dto import LocationDTO
from application.dto.input.job_input import JobSearchInputDTO
from application.dto.output.job_output import JobOutputDTO
from application.ports.repositories.interfaces import IJobRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from core.providers.scrapers.base import IScraperProvider


class SearchJobsUseCase(ApplicationUseCase[JobSearchInputDTO, List[JobOutputDTO]]):
    def __init__(
        self, scraper: IScraperProvider, job_repo: IJobRepository, uow: IUnitOfWork
    ):
        self._scraper = scraper
        self._job_repo = job_repo
        self._uow = uow

    def validate_input(self, input_dto: JobSearchInputDTO):
        if input_dto.limit > 100:
            return "Search limit cannot exceed 100."
        return None

    async def _run(self, input_dto: JobSearchInputDTO) -> Result[List[JobOutputDTO]]:
        # 1. Dispatch to Scraper Provider
        raw_jobs = await self._scraper.search(
            query=input_dto.query, location=input_dto.location, limit=input_dto.limit
        )

        # 2. Provider handles its own SDK-to-Domain mapping
        domain_jobs_create = self._scraper.normalize(raw_jobs)

        # 3. Map to Output DTOs (Simplified for this MVP)
        outputs = []
        for j in domain_jobs_create:
            outputs.append(
                JobOutputDTO(
                    id=j.job_id_raw,
                    title=j.title,
                    company_name=j.company_name,
                    location=LocationDTO(
                        city=j.location,
                        country="Unknown",
                        is_remote="remote" in j.location.lower(),
                    ),
                    url=j.url,
                    salary_range=j.salary_raw,
                )
            )

        return Result.ok(outputs)
