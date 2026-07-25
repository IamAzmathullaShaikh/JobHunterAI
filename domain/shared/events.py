import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

from domain.shared.value_objects import DomainId


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""

    aggregate_id: DomainId
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResumeCreated(DomainEvent):
    pass


@dataclass(frozen=True)
class ResumeUpdated(DomainEvent):
    pass


@dataclass(frozen=True)
class ApplicationSubmitted(DomainEvent):
    pass


@dataclass(frozen=True)
class ApplicationRejected(DomainEvent):
    pass


@dataclass(frozen=True)
class InterviewScheduled(DomainEvent):
    pass


@dataclass(frozen=True)
class InterviewCompleted(DomainEvent):
    pass


@dataclass(frozen=True)
class JobMatched(DomainEvent):
    job_id: DomainId
    score: float


@dataclass(frozen=True)
class CandidateSkillAdded(DomainEvent):
    skill_name: str
