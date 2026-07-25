from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateApplicationInputDTO:
    candidate_id: str
    job_id: str


@dataclass(frozen=True)
class UpdateApplicationStatusInputDTO:
    application_id: str
    new_status: str
    notes: Optional[str] = None
