from application.dto.input.application_input import CreateApplicationInputDTO
from application.dto.output.application_output import ApplicationOutputDTO
from application.mappers.application_mapper import ApplicationMapper
from application.ports.repositories.interfaces import IApplicationRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.value_objects import ApplicationId, CandidateId, JobId
from domain.tracking.application import Application


class CreateApplicationUseCase(
    ApplicationUseCase[CreateApplicationInputDTO, ApplicationOutputDTO]
):
    def __init__(self, application_repo: IApplicationRepository, uow: IUnitOfWork):
        self._application_repo = application_repo
        self._uow = uow

    async def _run(
        self, input_dto: CreateApplicationInputDTO
    ) -> Result[ApplicationOutputDTO]:
        app = Application(
            id=ApplicationId(),
            candidate_id=CandidateId.from_str(input_dto.candidate_id),
            job_id=JobId.from_str(input_dto.job_id),
        )

        async with self._uow:
            await self._application_repo.save(app)
            await self._uow.commit()

        return Result.ok(ApplicationMapper.to_output_dto(app))
