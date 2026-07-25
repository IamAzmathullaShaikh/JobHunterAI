from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class JobSearchInputDTO:
    query: str
    location: str = "Remote"
    limit: int = 20


@dataclass(frozen=True)
class CalculateMatchInputDTO:
    candidate_id: str
    job_id: str
