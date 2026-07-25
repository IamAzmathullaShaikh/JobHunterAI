import pytest

from domain.shared.enums import ApplicationStatus
from domain.shared.exceptions import BusinessRuleViolationError
from domain.shared.value_objects import ApplicationId, CandidateId, JobId
from domain.tracking.application import Application


def test_application_rejected_terminal():
    app = Application(id=ApplicationId(), candidate_id=CandidateId(), job_id=JobId())
    app.update_status(ApplicationStatus.APPLIED)
    app.reject("Not a good fit")

    # Violation: Reject is terminal
    with pytest.raises(BusinessRuleViolationError):
        app.update_status(ApplicationStatus.INTERVIEWING)


def test_application_valid_flow():
    app = Application(id=ApplicationId(), candidate_id=CandidateId(), job_id=JobId())
    assert app.status == ApplicationStatus.IDENTIFIED

    app.update_status(ApplicationStatus.APPLIED)
    assert app.status == ApplicationStatus.APPLIED

    app.update_status(ApplicationStatus.INTERVIEWING)
    assert len(app.timeline.events) == 2


def test_application_invalid_transition():
    app = Application(id=ApplicationId(), candidate_id=CandidateId(), job_id=JobId())
    # Identified -> Interviewing is not allowed directly
    with pytest.raises(BusinessRuleViolationError):
        app.update_status(ApplicationStatus.INTERVIEWING)
