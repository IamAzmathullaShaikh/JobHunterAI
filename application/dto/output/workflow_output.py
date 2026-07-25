from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class WorkflowHistoryDTO:
    timestamp: str
    previous_state: str
    new_state: str
    actor: str
    reason: Optional[str]


@dataclass(frozen=True)
class InterviewDTO:
    id: str
    scheduled_at: str
    status: str
    location: Optional[str]


@dataclass(frozen=True)
class OfferDTO:
    id: str
    salary: float
    currency: str
    status: str
    expires_at: Optional[str]


@dataclass(frozen=True)
class ApplicationWorkflowDTO:
    id: str
    status: str
    days_in_stage: int
    history: List[WorkflowHistoryDTO]
    interviews: List[InterviewDTO]
    offer: Optional[OfferDTO] = None
