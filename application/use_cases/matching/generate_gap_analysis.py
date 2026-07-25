from application.dto.input.job_input import CalculateMatchInputDTO
from application.dto.output.matching_output import (GapReportDTO,
                                                    RecommendationDTO)
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.matching.gap_analysis import GapAnalysisService
from domain.shared.value_objects import CandidateId, JobId


class GenerateGapAnalysisUseCase(
    ApplicationUseCase[CalculateMatchInputDTO, GapReportDTO]
):
    """
    Generates a structured report on the 'gaps' between a candidate and a job.
    """

    def __init__(self, candidate_repo: ICandidateRepository, job_repo: IJobRepository):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo

    async def _run(self, input_dto: CalculateMatchInputDTO) -> Result[GapReportDTO]:
        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(input_dto.candidate_id)
        )
        job = await self._job_repo.get_by_id(JobId.from_str(input_dto.job_id))

        if not candidate:
            return Result.not_found("Candidate not found.")
        if not job:
            return Result.not_found("Job not found.")

        gap = GapAnalysisService.generate(candidate, job)

        output = GapReportDTO(
            job_id=str(job.id),
            missing_skills=gap.missing_skills,
            missing_keywords=gap.missing_keywords,
            weak_areas=gap.weak_areas,
            recommendations=[
                RecommendationDTO(
                    category=r.category, message=r.message, impact=r.impact
                )
                for r in gap.recommendations
            ],
        )

        return Result.ok(output)
