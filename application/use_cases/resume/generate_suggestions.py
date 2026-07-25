from typing import List

from application.dto.output.resume_output import ResumeSuggestionDTO
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IResumeRepository)
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.analysis import ResumeSuggestionService
from domain.shared.value_objects import CandidateId


class GenerateResumeSuggestionsUseCase(
    ApplicationUseCase[str, List[ResumeSuggestionDTO]]
):
    """
    Generates rule-based improvement suggestions for a resume.
    """

    def __init__(
        self, resume_repo: IResumeRepository, candidate_repo: ICandidateRepository
    ):
        self._resume_repo = resume_repo
        self._candidate_repo = candidate_repo

    async def _run(self, resume_id: str) -> Result[List[ResumeSuggestionDTO]]:
        resume = await self._resume_repo.get_by_id(resume_id)
        if not resume:
            return Result.not_found("Resume not found.")

        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(resume.candidate_id)
        )
        if not candidate:
            return Result.infra_fail("Candidate link broken.")

        raw_suggestions = ResumeSuggestionService.generate_suggestions(
            resume, candidate
        )
        dtos = [ResumeSuggestionDTO(**s) for s in raw_suggestions]
        return Result.ok(dtos)

    async def execute(self, resume_id: str) -> Result[List[ResumeSuggestionDTO]]:
        return await self._run(resume_id)
