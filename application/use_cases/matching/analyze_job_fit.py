from application.dto.input.job_input import CalculateMatchInputDTO
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.value_objects import CandidateId, JobId


class AnalyzeJobFitUseCase(ApplicationUseCase[CalculateMatchInputDTO, dict]):
    """
    Performs a deep-dive analysis of why a candidate fits or doesn't fit a job.
    """

    def __init__(self, candidate_repo: ICandidateRepository, job_repo: IJobRepository):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo

    async def _run(self, input_dto: CalculateMatchInputDTO) -> Result[dict]:
        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(input_dto.candidate_id)
        )
        job = await self._job_repo.get_by_id(JobId.from_str(input_dto.job_id))

        if not candidate:
            return Result.not_found("Candidate not found.")
        if not job:
            return Result.not_found("Job not found.")

        # In a real implementation, this would orchestrate multiple services
        # to produce a rich qualitative report.
        from domain.services.matching.gap_analysis import GapAnalysisService

        gap = GapAnalysisService.generate(candidate, job)

        return Result.ok(
            {
                "job_title": job.title,
                "candidate_name": candidate.full_name,
                "weak_areas": gap.weak_areas,
                "missing_skills": gap.missing_skills,
            }
        )
