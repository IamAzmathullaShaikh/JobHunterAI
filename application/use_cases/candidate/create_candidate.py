from application.dto.input.candidate_input import CreateCandidateInputDTO
from application.dto.output.candidate_output import CandidateOutputDTO
from application.mappers.candidate_mapper import CandidateMapper
from application.ports.repositories.interfaces import ICandidateRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.profile.candidate import Candidate
from domain.shared.value_objects import (CandidateId, ContactInfo,
                                         EmailAddress, PhoneNumber)


class CreateCandidateUseCase(
    ApplicationUseCase[CreateCandidateInputDTO, CandidateOutputDTO]
):
    def __init__(self, candidate_repo: ICandidateRepository, uow: IUnitOfWork):
        self._candidate_repo = candidate_repo
        self._uow = uow

    def validate_input(self, input_dto: CreateCandidateInputDTO):
        if not input_dto.full_name or len(input_dto.full_name) < 2:
            return "Full name must be at least 2 characters long."
        return None

    async def _run(
        self, input_dto: CreateCandidateInputDTO
    ) -> Result[CandidateOutputDTO]:
        # 1. Check if already exists
        existing = await self._candidate_repo.find_by_email(input_dto.email)
        if existing:
            return Result.business_fail(
                f"Candidate with email {input_dto.email} already exists."
            )

        # 2. Create Aggregate (Domain logic handles detailed validation)
        email = EmailAddress(input_dto.email)
        phone = PhoneNumber(input_dto.phone) if input_dto.phone else None

        contact = ContactInfo(
            email=email, phone=phone, linkedin_url=input_dto.linkedin_url
        )

        candidate = Candidate(
            id=CandidateId(), _full_name=input_dto.full_name, _contact_info=contact
        )

        # 3. Persist within Unit of Work
        async with self._uow:
            await self._candidate_repo.save(candidate)
            await self._uow.commit()

        # 4. Return Output via Mapper
        return Result.ok(CandidateMapper.to_output_dto(candidate))
