from typing import List

from application.dto.output.resume_output import ResumeSuggestionDTO
from application.results.result import Result
from application.use_cases.resume.generate_suggestions import \
    GenerateResumeSuggestionsUseCase


class ResumeSuggestionService:
    def __init__(self, suggest_uc: GenerateResumeSuggestionsUseCase):
        self._suggest_uc = suggest_uc

    async def suggest(self, resume_id: str) -> Result[List[ResumeSuggestionDTO]]:
        return await self._suggest_uc.execute(resume_id)
