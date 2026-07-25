from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class CandidateOutputDTO:
    id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    total_experience: float = 0.0
