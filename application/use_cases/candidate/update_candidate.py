from application.dto.input.candidate_input import UpdateCandidateInputDTO
from application.dto.output.candidate_output import CandidateOutputDTO
from application.mappers.candidate_mapper import CandidateMapper
from application.ports.repositories.interfaces import ICandidateRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.value_objects import CandidateId, ContactInfo, PhoneNumber


class UpdateCandidateUseCase(
    ApplicationUseCase[UpdateCandidateInputDTO, CandidateOutputDTO]
):
    def __init__(self, candidate_repo: ICandidateRepository, uow: IUnitOfWork):
        self._candidate_repo = candidate_repo
        self._uow = uow

    async def _run(
        self, candidate_id: str, input_dto: UpdateCandidateInputDTO
    ) -> Result[CandidateOutputDTO]:
        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(candidate_id)
        )
        if not candidate:
            return Result.not_found("Candidate not found.")

        # Update domain object
        if input_dto.full_name:
            candidate._full_name = input_dto.full_name

        if input_dto.phone or input_dto.linkedin_url:
            new_contact = ContactInfo(
                email=candidate.contact_info.email,
                phone=(
                    PhoneNumber(input_dto.phone)
                    if input_dto.phone
                    else candidate.contact_info.phone
                ),
                linkedin_url=input_dto.linkedin_url
                or candidate.contact_info.linkedin_url,
            )
            candidate.update_contact(new_contact)

        async with self._uow:
            await self._candidate_repo.save(candidate)
            await self._uow.commit()

        return Result.ok(CandidateMapper.to_output_dto(candidate))

    # Overriding execute because of additional candidate_id param for this simple MVP
    # In a full design, candidate_id would be part of input_dto
    async def execute(
        self, candidate_id: str, input_dto: UpdateCandidateInputDTO
    ) -> Result[CandidateOutputDTO]:
        return await self._run(candidate_id, input_dto)
