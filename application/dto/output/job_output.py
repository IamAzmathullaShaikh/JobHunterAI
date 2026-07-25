from dataclasses import dataclass
from typing import List, Optional

from application.dto.common.location_dto import LocationDTO


@dataclass(frozen=True)
class JobOutputDTO:
    id: str
    title: str
    company_name: str
    location: LocationDTO
    url: str
    salary_range: Optional[str] = None
    is_open: bool = True


@dataclass(frozen=True)
class MatchResultDTO:
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
    fit_summary: str
