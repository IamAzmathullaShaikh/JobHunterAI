import logging

from application.ports.repositories.interfaces import IApplicationRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.enums import ApplicationStatus
from domain.shared.value_objects import ApplicationId

logger = logging.getLogger(__name__)


class SubmitApplicationUseCase(ApplicationUseCase[str, str]):
    def __init__(self, application_repo: IApplicationRepository, uow: IUnitOfWork):
        self._application_repo = application_repo
        self._uow = uow

    async def _run(self, application_id: str) -> Result[str]:
        app = await self._application_repo.get_by_id(
            ApplicationId.from_str(application_id)
        )
        if not app:
            return Result.not_found("Application not found.")

        # 1. Domain logic
        app.submit()

        # 2. Persist
        async with self._uow:
            await self._application_repo.save(app)
            await self._uow.commit()

        return Result.ok("Application submitted successfully.")

    async def execute(self, application_id: str) -> Result[str]:
        return await self._run(application_id)
