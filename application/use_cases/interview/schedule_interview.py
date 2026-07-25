from application.dto.input.interview_input import ScheduleInterviewInputDTO
from application.ports.repositories.interfaces import IApplicationRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.value_objects import ApplicationId, InterviewId


class ScheduleInterviewUseCase(ApplicationUseCase[ScheduleInterviewInputDTO, str]):
    def __init__(self, application_repo: IApplicationRepository, uow: IUnitOfWork):
        self._application_repo = application_repo
        self._uow = uow

    async def _run(self, input_dto: ScheduleInterviewInputDTO) -> Result[str]:
        app_id = ApplicationId.from_str(input_dto.application_id)
        application = await self._application_repo.get_by_id(app_id)

        if not application:
            return Result.not_found("Application not found.")

        application.schedule_interview(
            interview_id=InterviewId(), scheduled_at=input_dto.scheduled_at
        )

        async with self._uow:
            await self._application_repo.save(application)
            await self._uow.commit()

        return Result.ok("Interview scheduled successfully.")
