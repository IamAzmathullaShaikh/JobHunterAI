from application.dto.input.application_input import \
    UpdateApplicationStatusInputDTO
from application.dto.output.application_output import ApplicationOutputDTO
from application.mappers.application_mapper import ApplicationMapper
from application.ports.repositories.interfaces import IApplicationRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.enums import ApplicationStatus
from domain.shared.value_objects import ApplicationId


class UpdateApplicationStatusUseCase(
    ApplicationUseCase[UpdateApplicationStatusInputDTO, ApplicationOutputDTO]
):
    def __init__(self, application_repo: IApplicationRepository, uow: IUnitOfWork):
        self._application_repo = application_repo
        self._uow = uow

    async def _run(
        self, input_dto: UpdateApplicationStatusInputDTO
    ) -> Result[ApplicationOutputDTO]:
        app_id = ApplicationId.from_str(input_dto.application_id)
        application = await self._application_repo.get_by_id(app_id)

        if not application:
            return Result.not_found(
                f"Application {input_dto.application_id} not found."
            )

        # Trigger domain state machine
        new_status = ApplicationStatus(input_dto.new_status)
        application.update_status(new_status, input_dto.notes)

        async with self._uow:
            await self._application_repo.save(application)
            await self._uow.commit()

        return Result.ok(ApplicationMapper.to_output_dto(application))
