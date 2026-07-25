from datetime import datetime, timedelta

import pytest

from domain.shared.enums import ApplicationStatus
from domain.shared.exceptions import BusinessRuleViolationError
from domain.shared.value_objects import (ApplicationId, CandidateId,
                                         InterviewId, JobId)
from domain.tracking.application import Application


def test_application_full_lifecycle():
    app = Application(id=ApplicationId(), candidate_id=CandidateId(), job_id=JobId())
    assert app.status == ApplicationStatus.DRAFT

    # 1. Draft -> Ready
    app.update_status(ApplicationStatus.READY)

    # 2. Ready -> Submitted
    app.submit()
    assert app.status == ApplicationStatus.SUBMITTED

    # 3. Submitted -> Screening
    app.update_status(ApplicationStatus.SCREENING)

    # 4. Schedule Interview (Screening -> Interviewing)
    app.schedule_interview(InterviewId(), datetime.now() + timedelta(days=1))
    assert app.status == ApplicationStatus.INTERVIEWING

    # 5. Interviewing -> Offer
    app.update_status(ApplicationStatus.OFFER_RECEIVED)
    assert app.status == ApplicationStatus.OFFER_RECEIVED


def test_illegal_state_transition():
    app = Application(id=ApplicationId(), candidate_id=CandidateId(), job_id=JobId())

    # Draft -> Interviewing is not allowed
    with pytest.raises(BusinessRuleViolationError):
        app.update_status(ApplicationStatus.INTERVIEWING)


def test_terminal_states_prevent_actions():
    app = Application(id=ApplicationId(), candidate_id=CandidateId(), job_id=JobId())
    app.update_status(ApplicationStatus.WITHDRAWN)

    with pytest.raises(BusinessRuleViolationError):
        app.schedule_interview(InterviewId(), datetime.now())


def test_workflow_history_immutability():
    app = Application(id=ApplicationId(), candidate_id=CandidateId(), job_id=JobId())
    app.update_status(ApplicationStatus.READY)

    history = app.history[0]
    assert history.previous_state == ApplicationStatus.DRAFT
    assert history.new_state == ApplicationStatus.READY
    assert history.actor == "system"
