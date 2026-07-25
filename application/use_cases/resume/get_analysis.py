from application.dto.output.resume_output import (ResumeAnalysisOutputDTO,
                                                  ResumeScoreDTO)
from application.ports.repositories.interfaces import IResumeRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from application.use_cases.resume.generate_suggestions import \
    GenerateResumeSuggestionsUseCase
from application.use_cases.resume.score_resume import ScoreResumeUseCase


class GetResumeAnalysisUseCase(ApplicationUseCase[str, ResumeAnalysisOutputDTO]):
    """
    Aggregates scoring and suggestions into a final Analysis report.
    """

    def __init__(
        self,
        resume_repo: IResumeRepository,
        score_uc: ScoreResumeUseCase,
        suggest_uc: GenerateResumeSuggestionsUseCase,
    ):
        self._resume_repo = resume_repo
        self._score_uc = score_uc
        self._suggest_uc = suggest_uc

    async def _run(self, resume_id: str) -> Result[ResumeAnalysisOutputDTO]:
        resume = await self._resume_repo.get_by_id(resume_id)
        if not resume:
            return Result.not_found("Resume not found.")

        score_res = await self._score_uc.execute(resume_id)
        suggest_res = await self._suggest_uc.execute(resume_id)

        if score_res.is_failure:
            return score_res
        if suggest_res.is_failure:
            return suggest_res

        return Result.ok(
            ResumeAnalysisOutputDTO(
                resume_id=str(resume.id),
                version=resume.version_count,
                score=score_res.unwrap(),
                strengths=[],  # Logic to extract from score/suggestions
                weaknesses=[],
                suggestions=suggest_res.unwrap(),
                is_ready_for_applications=score_res.unwrap().overall_score > 0.7,
            )
        )

    async def execute(self, resume_id: str) -> Result[ResumeAnalysisOutputDTO]:
        return await self._run(resume_id)
