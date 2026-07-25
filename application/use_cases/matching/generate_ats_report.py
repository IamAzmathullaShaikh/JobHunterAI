from application.dto.output.matching_output import (ATSReportDTO,
                                                    RecommendationDTO)
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IResumeRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.matching.ats_scoring import ATSScoringService
from domain.shared.value_objects import CandidateId


class GenerateATSReportUseCase(ApplicationUseCase[str, ATSReportDTO]):
    """
    Evaluates a resume against common ATS rules.
    """

    def __init__(
        self, resume_repo: IResumeRepository, candidate_repo: ICandidateRepository
    ):
        self._resume_repo = resume_repo
        self._candidate_repo = candidate_repo

    async def _run(self, resume_id: str) -> Result[ATSReportDTO]:
        resume = await self._resume_repo.get_by_id(resume_id)
        if not resume:
            return Result.not_found("Resume not found.")

        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(resume.candidate_id)
        )
        if not candidate:
            return Result.infra_fail("Candidate link broken.")

        report = ATSScoringService.analyze(resume, candidate)

        output = ATSReportDTO(
            resume_id=str(resume.id),
            overall_score=report.overall_score,
            section_scores=report.section_scores,
            recommendations=[
                RecommendationDTO(
                    category=r.category, message=r.message, impact=r.impact
                )
                for r in report.recommendations
            ],
        )

        return Result.ok(output)

    async def execute(self, resume_id: str) -> Result[ATSReportDTO]:
        return await self._run(resume_id)
