import asyncio
from typing import List

from application.dto.input.job_input import CalculateMatchInputDTO
from application.dto.output.matching_output import JobMatchDTO
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from application.use_cases.matching.match_resume_to_job import \
    MatchResumeToJobUseCase


class BatchMatchJobsUseCase(ApplicationUseCase[tuple, List[JobMatchDTO]]):
    """
    Efficiently matches a candidate against multiple jobs.
    """

    def __init__(self, match_one_uc: MatchResumeToJobUseCase):
        self._match_one_uc = match_one_uc

    async def _run(self, input_data: tuple) -> Result[List[JobMatchDTO]]:
        candidate_id, job_ids = input_data

        # Parallel execution where safe (IO bound calls to repos)
        tasks = [
            self._match_one_uc.execute(
                CalculateMatchInputDTO(candidate_id=candidate_id, job_id=jid)
            )
            for jid in job_ids
        ]

        results = await asyncio.gather(*tasks)

        matches = []
        for res in results:
            if res.is_success:
                matches.append(res.unwrap())

        # Sort by overall score descending
        matches.sort(key=lambda x: x.overall_score, reverse=True)

        return Result.ok(matches)

    async def execute(
        self, candidate_id: str, job_ids: List[str]
    ) -> Result[List[JobMatchDTO]]:
        return await self._run((candidate_id, job_ids))
