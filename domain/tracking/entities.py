from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from domain.shared.enums import InterviewStatus
from domain.shared.value_objects import ApplicationId, InterviewId


@dataclass
class Interview:
    id: InterviewId
    application_id: ApplicationId
    scheduled_at: datetime
    status: InterviewStatus = InterviewStatus.SCHEDULED
    location: Optional[str] = None  # Link or Address
    interviewer_names: List[str] = field(default_factory=list)
    feedback_notes: Optional[str] = None

    def complete(self, notes: str):
        self.status = InterviewStatus.COMPLETED
        self.feedback_notes = notes

    def cancel(self):
        self.status = InterviewStatus.CANCELLED


@dataclass(frozen=True)
class StatusHistory:
    status: str
    changed_at: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None


@dataclass
class ApplicationTimeline:
    _events: List[StatusHistory] = field(default_factory=list)

    @property
    def events(self) -> Tuple[StatusHistory, ...]:
        return tuple(self._events)

    def add_event(self, status: str, notes: Optional[str] = None):
        self._events.append(StatusHistory(status=status, notes=notes))
