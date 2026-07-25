from application.dto.output.analytics_output import (DashboardDTO,
                                                     ExecutiveSummaryDTO)
from application.results.result import Result
from application.use_cases.analytics.generate_dashboard import \
    GenerateCandidateDashboardUseCase
from application.use_cases.analytics.generate_executive_summary import \
    GenerateExecutiveSummaryUseCase


class AnalyticsService:
    def __init__(
        self,
        dashboard_uc: GenerateCandidateDashboardUseCase,
        summary_uc: GenerateExecutiveSummaryUseCase,
    ):
        self._dashboard_uc = dashboard_uc
        self._summary_uc = summary_uc

    async def get_full_status_report(self, candidate_id: str) -> Result[dict]:
        dash_res = await self._dashboard_uc.execute(candidate_id)
        if dash_res.is_failure:
            return dash_res

        summary_res = await self._summary_uc.execute(dash_res.unwrap())

        return Result.ok(
            {
                "dashboard": dash_res.unwrap(),
                "summary": summary_res.unwrap() if summary_res.is_success else None,
            }
        )
