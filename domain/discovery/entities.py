from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from domain.shared.enums import EmploymentType, ExperienceLevel, WorkMode
from domain.shared.value_objects import (CandidateId, JobId, Location,
                                         SalaryRange)


@dataclass(frozen=True)
class JobRequirement:
    name: str
    is_required: bool = True
    category: str = "general"  # skills, experience, education, etc.


@dataclass
class JobDescription:
    raw_text: str
    parsed_at: datetime = field(default_factory=datetime.now)
    requirements: List[JobRequirement] = field(default_factory=list)


@dataclass
class Job:
    id: JobId
    company_id: str
    title: str
    description: str
    url: str
    location: Location
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    work_mode: WorkMode = WorkMode.ONSITE
    experience_level: Optional[ExperienceLevel] = None
    salary_range: Optional[SalaryRange] = None
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    date_posted: Optional[datetime] = None
    date_scraped: datetime = field(default_factory=datetime.now)
    _is_open: bool = True

    def is_open(self) -> bool:
        return self._is_open

    def close(self):
        self._is_open = False

    def requires_skill(self, skill_name: str) -> bool:
        return any(s.lower() == skill_name.lower() for s in self.required_skills)

    def matches_location(self, target_location: Location) -> bool:
        return self.location.matches(target_location)

    def has_salary(self) -> bool:
        return self.salary_range is not None


@dataclass(frozen=True)
class MatchBreakdown:
    skills_score: float
    experience_score: float
    education_score: float
    keywords_score: float
    location_score: float
    salary_score: float
    other_score: float = 0.0


@dataclass(frozen=True)
class MatchResult:
    job_id: JobId
    candidate_id: CandidateId
    overall_score: float  # 0.0 to 1.0
    breakdown: MatchBreakdown
    matched_skills: List[str]
    missing_skills: List[str]
    fit_summary: str

    # Explainability & Metadata
    evidence: Dict[str, Any] = field(default_factory=dict)
    improvement_suggestions: List[str] = field(default_factory=list)
    confidence: float = 1.0

    configuration_version: str = "1.0.0"
    matching_strategy: str = "weighted_linear"
    weights_version: str = "default"

    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class Recommendation:
    category: str
    message: str
    impact: str  # high, medium, low


@dataclass(frozen=True)
class GapAnalysis:
    job_id: JobId
    candidate_id: CandidateId
    missing_skills: List[str]
    missing_keywords: List[str]
    weak_areas: List[str]
    recommendations: List[Recommendation]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ATSScore:
    resume_id: str
    overall_score: float
    section_scores: Dict[str, float]
    recommendations: List[Recommendation]
    analyzed_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class SearchCriteria:
    query: str
    location: Optional[Location] = None
    remote_only: bool = False
    min_salary: Optional[float] = None
    job_type: Optional[EmploymentType] = None
