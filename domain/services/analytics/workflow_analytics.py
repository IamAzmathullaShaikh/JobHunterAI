from typing import Dict, List

from domain.shared.analytics_models import KPI
from domain.shared.enums import ApplicationStatus
from domain.tracking.application import Application


class WorkflowAnalyticsService:
    """
    Pure logic for application funnel and pipeline velocity.
    """

    @staticmethod
    def calculate_funnel_metrics(applications: List[Application]) -> Dict[str, int]:
        counts = {status.value: 0 for status in ApplicationStatus}
        for app in applications:
            counts[app.status.value] += 1
        return counts

    @staticmethod
    def calculate_conversion_rate(applications: List[Application]) -> float:
        total = len(applications)
        if total == 0:
            return 0.0

        # Interview rate: Applications that reached INTERVIEWING stage
        reached_interview = [
            app
            for app in applications
            if any(h.new_state == ApplicationStatus.INTERVIEWING for h in app.history)
        ]

        return round(len(reached_interview) / total, 2)

    @staticmethod
    def calculate_velocity_kpi(applications: List[Application]) -> KPI:
        # Average days in current stage for active apps
        active = [
            app
            for app in applications
            if app.status
            not in [ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN]
        ]
        if not active:
            return KPI(
                id="pipeline_velocity",
                name="Avg Days in Stage",
                current_value=0.0,
                unit="days",
            )

        avg_days = sum(app.days_in_current_stage for app in active) / len(active)

        return KPI(
            id="pipeline_velocity",
            name="Avg Days in Stage",
            current_value=round(avg_days, 1),
            target_value=5.0,  # Target: move stages every 5 days
            unit="days",
        )
