from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from domain.shared.enums import ApplicationStatus, InterviewStatus
from domain.shared.exceptions import BusinessRuleViolationError
from domain.shared.value_objects import (ApplicationId, CandidateId,
                                         InterviewId, JobId)
from domain.tracking.entities import (ApplicationTimeline, Interview,
                                      StatusHistory)
from domain.tracking.offer import Offer


@dataclass(frozen=True)
class WorkflowHistory:
    """Immutable record of a state transition."""

    timestamp: datetime
    previous_state: ApplicationStatus
    new_state: ApplicationStatus
    actor: str
    reason: Optional[str] = None
    notes: Optional[str] = None
    correlation_id: Optional[str] = None


@dataclass
class Application:
    id: ApplicationId
    candidate_id: CandidateId
    job_id: JobId
    _status: ApplicationStatus = ApplicationStatus.DRAFT
    _timeline: ApplicationTimeline = field(default_factory=ApplicationTimeline)
    _interviews: List[Interview] = field(default_factory=list)
    _history: List[WorkflowHistory] = field(default_factory=list)
    _offer: Optional[Offer] = None

    _applied_at: Optional[datetime] = None
    _created_at: datetime = field(default_factory=datetime.now)

    # --- Full Lifecycle State Machine (Class Level) ---
    _VALID_TRANSITIONS = {
        ApplicationStatus.DRAFT: {ApplicationStatus.READY, ApplicationStatus.WITHDRAWN},
        ApplicationStatus.READY: {
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.SUBMITTED: {
            ApplicationStatus.SCREENING,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.SCREENING: {
            ApplicationStatus.INTERVIEWING,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.INTERVIEWING: {
            ApplicationStatus.TECHNICAL_INTERVIEW,
            ApplicationStatus.HR_INTERVIEW,
            ApplicationStatus.OFFER_RECEIVED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.TECHNICAL_INTERVIEW: {
            ApplicationStatus.HR_INTERVIEW,
            ApplicationStatus.OFFER_RECEIVED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.HR_INTERVIEW: {
            ApplicationStatus.OFFER_RECEIVED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.OFFER_RECEIVED: {
            ApplicationStatus.OFFER_ACCEPTED,
            ApplicationStatus.OFFER_REJECTED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.OFFER_ACCEPTED: {
            ApplicationStatus.JOINED,
            ApplicationStatus.WITHDRAWN,
        },
        ApplicationStatus.JOINED: set(),  # Terminal Success
        ApplicationStatus.REJECTED: set(),  # Terminal Failure
        ApplicationStatus.WITHDRAWN: set(),  # Terminal Cancellation
        ApplicationStatus.EXPIRED: set(),  # Terminal
        ApplicationStatus.CANCELLED: set(),  # Terminal
    }

    @property
    def status(self) -> ApplicationStatus:
        return self._status

    @property
    def interviews(self) -> Tuple[Interview, ...]:
        return tuple(self._interviews)

    @property
    def history(self) -> Tuple[WorkflowHistory, ...]:
        return tuple(self._history)

    def update_status(
        self,
        new_status: ApplicationStatus,
        actor: str = "system",
        reason: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        if new_status == self._status:
            return

        allowed = self._VALID_TRANSITIONS.get(self._status, set())
        if new_status not in allowed:
            raise BusinessRuleViolationError(
                f"Invalid transition from {self._status.value} to {new_status.value}"
            )

        # Record History
        record = WorkflowHistory(
            timestamp=datetime.now(),
            previous_state=self._status,
            new_state=new_status,
            actor=actor,
            reason=reason,
            notes=notes,
        )
        self._history.append(record)

        self._status = new_status
        self._timeline.add_event(new_status.value, notes)

        if new_status == ApplicationStatus.SUBMITTED and not self._applied_at:
            self._applied_at = datetime.now()

    def submit(self):
        self.update_status(
            ApplicationStatus.SUBMITTED, reason="Candidate submitted application"
        )

    def reject(self, reason: str):
        self.update_status(ApplicationStatus.REJECTED, reason=reason)

    def withdraw(self, reason: str):
        self.update_status(ApplicationStatus.WITHDRAWN, reason=reason)

    def schedule_interview(
        self, interview_id: InterviewId, scheduled_at: datetime
    ) -> Interview:
        if self._status in [ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN]:
            raise BusinessRuleViolationError(
                "Cannot schedule interview for a terminal application."
            )

        new_interview = Interview(
            id=interview_id, application_id=self.id, scheduled_at=scheduled_at
        )
        self._interviews.append(new_interview)
        self.update_status(
            ApplicationStatus.INTERVIEWING,
            notes=f"Interview scheduled for {scheduled_at}",
        )
        return new_interview

    def receive_offer(self, offer: Offer):
        self._offer = offer
        self.update_status(ApplicationStatus.OFFER_RECEIVED)

    def accept_offer(self):
        if not self._offer:
            raise BusinessRuleViolationError("No offer to accept.")
        self._offer.accept()
        self.update_status(ApplicationStatus.OFFER_ACCEPTED)

    @property
    def days_in_current_stage(self) -> int:
        last_change = self._history[-1].timestamp if self._history else self._created_at
        return (datetime.now() - last_change).days
