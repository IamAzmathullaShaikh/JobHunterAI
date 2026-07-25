from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MatchBreakdownDTO:
    skills: float
    experience: float
    education: float
    keywords: float
    location: float
    salary: float


@dataclass(frozen=True)
class JobMatchDTO:
    job_id: str
    overall_score: float
    breakdown: MatchBreakdownDTO
    matched_skills: List[str]
    missing_skills: List[str]
    fit_summary: str


@dataclass(frozen=True)
class RecommendationDTO:
    category: str
    message: str
    impact: str


@dataclass(frozen=True)
class GapReportDTO:
    job_id: str
    missing_skills: List[str]
    missing_keywords: List[str]
    weak_areas: List[str]
    recommendations: List[RecommendationDTO]


@dataclass(frozen=True)
class ATSReportDTO:
    resume_id: str
    overall_score: float
    section_scores: Dict[str, float]
    recommendations: List[RecommendationDTO]
