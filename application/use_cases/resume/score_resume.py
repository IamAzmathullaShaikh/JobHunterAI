from application.dto.output.resume_output import ResumeScoreDTO
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IResumeRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.analysis import ResumeScoringService
from domain.shared.value_objects import CandidateId


class ScoreResumeUseCase(ApplicationUseCase[str, ResumeScoreDTO]):
    """
    Calculates deterministic quality scores for a resume version.
    """

    def __init__(
        self, resume_repo: IResumeRepository, candidate_repo: ICandidateRepository
    ):
        self._resume_repo = resume_repo
        self._candidate_repo = candidate_repo

    async def _run(self, resume_id: str) -> Result[ResumeScoreDTO]:
        resume = await self._resume_repo.get_by_id(resume_id)
        if not resume:
            return Result.not_found("Resume not found.")

        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(resume.candidate_id)
        )
        if not candidate:
            return Result.infra_fail("Candidate link broken.")

        score_data = ResumeScoringService.calculate_score(resume, candidate)
        return Result.ok(ResumeScoreDTO(**score_data))

    async def execute(self, resume_id: str) -> Result[ResumeScoreDTO]:
        return await self._run(resume_id)
