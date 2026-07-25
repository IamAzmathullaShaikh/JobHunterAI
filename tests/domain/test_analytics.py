from datetime import datetime, timedelta

import pytest

from domain.services.analytics.workflow_analytics import \
    WorkflowAnalyticsService
from domain.shared.enums import ApplicationStatus
from domain.shared.value_objects import ApplicationId, CandidateId, JobId
from domain.tracking.application import Application, WorkflowHistory


def test_funnel_metrics_calculation():
    c_id = CandidateId()
    j_id = JobId()

    app1 = Application(id=ApplicationId(), candidate_id=c_id, job_id=j_id)
    app1.update_status(ApplicationStatus.READY)
    app1.submit()  # transitions to submitted

    app2 = Application(id=ApplicationId(), candidate_id=c_id, job_id=j_id)
    app2.update_status(ApplicationStatus.READY)
    app2.submit()
    app2.update_status(ApplicationStatus.REJECTED)

    metrics = WorkflowAnalyticsService.calculate_funnel_metrics([app1, app2])

    assert metrics["submitted"] == 1
    assert metrics["rejected"] == 1
    assert metrics["draft"] == 0


def test_conversion_rate():
    c_id = CandidateId()
    j_id = JobId()

    # 2 apps, 1 reached interview
    app1 = Application(id=ApplicationId(), candidate_id=c_id, job_id=j_id)
    app1.update_status(ApplicationStatus.READY)
    app1.submit()
    app1.update_status(ApplicationStatus.SCREENING)
    app1.update_status(ApplicationStatus.INTERVIEWING)

    app2 = Application(id=ApplicationId(), candidate_id=c_id, job_id=j_id)

    rate = WorkflowAnalyticsService.calculate_conversion_rate([app1, app2])
    assert rate == 0.5


def test_pipeline_velocity():
    app = Application(id=ApplicationId(), candidate_id=CandidateId(), job_id=JobId())
    kpi = WorkflowAnalyticsService.calculate_velocity_kpi([app])
    assert kpi.id == "pipeline_velocity"
    assert kpi.current_value >= 0
