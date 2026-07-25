from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ApplicationOutputDTO:
    id: str
    candidate_id: str
    job_id: str
    status: str
    applied_at: Optional[str] = None
