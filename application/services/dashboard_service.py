from typing import Any, Dict, List, Optional

from application.dto.output.analytics_output import (KPIDTO, DashboardDTO,
                                                     RecommendationDTO,
                                                     TrendDTO)
from application.ports.repositories.interfaces import (IApplicationRepository,
                                                       ICandidateRepository,
                                                       IJobRepository)
from application.results.result import Result
from domain.services.analytics.match_analytics import MatchAnalyticsService
from domain.services.analytics.resume_analytics import ResumeAnalyticsService
from domain.services.analytics.workflow_analytics import \
    WorkflowAnalyticsService
from domain.services.recommendation.engine import RecommendationEngineService
from domain.shared.value_objects import CandidateId


class DashboardService:
    """
    Orchestrates data collection from repositories and invokes domain
    analytics services to build a unified dashboard.
    """

    def __init__(
        self,
        candidate_repo: ICandidateRepository,
        app_repo: IApplicationRepository,
        # match_repo: IMatchRepository (future)
    ):
        self._candidate_repo = candidate_repo
        self._app_repo = app_repo

    async def get_candidate_dashboard(self, candidate_id: str) -> Result[DashboardDTO]:
        c_id = CandidateId.from_str(candidate_id)
        candidate = await self._candidate_repo.get_by_id(c_id)
        if not candidate:
            return Result.not_found("Candidate not found.")

        apps = await self._app_repo.list_by_candidate(c_id)

        # 1. Calculate KPIs
        kpis = []

        # Resume KPI
        resume = candidate.latest_resume()
        if resume:
            resume_kpi = ResumeAnalyticsService.calculate_quality_kpi(resume, candidate)
            kpis.append(resume_kpi)

        # Velocity KPI
        velocity_kpi = WorkflowAnalyticsService.calculate_velocity_kpi(apps)
        kpis.append(velocity_kpi)

        # 2. Funnel & Conversion
        funnel = WorkflowAnalyticsService.calculate_funnel_metrics(apps)
        conversion = WorkflowAnalyticsService.calculate_conversion_rate(apps)

        # 3. Recommendations
        recs = RecommendationEngineService.generate_recommendations(candidate, kpis)

        # 4. Map to DTOs
        kpi_dtos = [
            KPIDTO(
                id=k.id,
                name=k.name,
                value=k.current_value,
                target=k.target_value,
                unit=k.unit,
                trend=(
                    TrendDTO(
                        direction=k.trend.direction.value,
                        delta=k.trend.delta_percentage,
                        previous=k.trend.previous_value,
                        current=k.trend.current_value,
                    )
                    if k.trend
                    else None
                ),
            )
            for k in kpis
        ]

        rec_dtos = [
            RecommendationDTO(
                priority=r.priority,
                category=r.category,
                message=r.message,
                impact=r.expected_impact,
            )
            for r in recs
        ]

        return Result.ok(
            DashboardDTO(
                kpis=kpi_dtos,
                recommendations=rec_dtos,
                funnel=funnel,
                conversion_rate=conversion,
            )
        )
