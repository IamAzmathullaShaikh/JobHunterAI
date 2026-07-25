from application.dto.input.job_input import CalculateMatchInputDTO
from application.dto.output.job_output import MatchResultDTO
from application.results.result import Result
from application.use_cases.matching.calculate_match import \
    CalculateJobMatchUseCase
from application.use_cases.matching.generate_cover_letter import \
    GenerateCoverLetterUseCase


class MatchingApplicationService:
    """Orchestrates matching and tailoring logic."""

    def __init__(
        self,
        match_uc: CalculateJobMatchUseCase,
        cover_letter_uc: GenerateCoverLetterUseCase,
    ):
        self._match_uc = match_uc
        self._cover_letter_uc = cover_letter_uc

    async def evaluate_fit(self, dto: CalculateMatchInputDTO) -> Result[MatchResultDTO]:
        return await self._match_uc.execute(dto)

    async def tailor_outreach(self, resume_id: str, jd: str) -> Result[str]:
        return await self._cover_letter_uc.execute(resume_id, jd)
