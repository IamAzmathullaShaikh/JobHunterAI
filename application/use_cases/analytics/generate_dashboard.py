from application.dto.output.analytics_output import DashboardDTO
from application.results.result import Result
from application.services.dashboard_service import DashboardService
from application.use_cases.base import ApplicationUseCase


class GenerateCandidateDashboardUseCase(ApplicationUseCase[str, DashboardDTO]):
    def __init__(self, dashboard_service: DashboardService):
        self._service = dashboard_service

    async def _run(self, candidate_id: str) -> Result[DashboardDTO]:
        return await self._service.get_candidate_dashboard(candidate_id)

    async def execute(self, candidate_id: str) -> Result[DashboardDTO]:
        return await self._run(candidate_id)
