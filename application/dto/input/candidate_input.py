from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateCandidateInputDTO:
    full_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None


@dataclass(frozen=True)
class UpdateCandidateInputDTO:
    full_name: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
