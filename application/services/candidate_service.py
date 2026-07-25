from application.dto.input.candidate_input import (CreateCandidateInputDTO,
                                                   UpdateCandidateInputDTO)
from application.dto.output.candidate_output import CandidateOutputDTO
from application.results.result import Result
from application.use_cases.candidate.create_candidate import \
    CreateCandidateUseCase
from application.use_cases.candidate.update_candidate import \
    UpdateCandidateUseCase


class CandidateApplicationService:
    """Orchestrates candidate-related workflows."""

    def __init__(
        self, create_uc: CreateCandidateUseCase, update_uc: UpdateCandidateUseCase
    ):
        self._create_uc = create_uc
        self._update_uc = update_uc

    async def register(
        self, dto: CreateCandidateInputDTO
    ) -> Result[CandidateOutputDTO]:
        return await self._create_uc.execute(dto)

    async def update_profile(
        self, candidate_id: str, dto: UpdateCandidateInputDTO
    ) -> Result[CandidateOutputDTO]:
        return await self._update_uc.execute(candidate_id, dto)
