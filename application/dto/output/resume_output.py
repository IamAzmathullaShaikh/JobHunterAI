from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ResumeScoreDTO:
    overall_score: float
    completeness_score: float
    formatting_score: float
    keyword_score: float


@dataclass(frozen=True)
class ResumeSuggestionDTO:
    category: str  # "skills", "experience", "formatting", "contact"
    message: str
    impact: str  # "high", "medium", "low"


@dataclass(frozen=True)
class ResumeAnalysisOutputDTO:
    resume_id: str
    version: int
    score: ResumeScoreDTO
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[ResumeSuggestionDTO]
    is_ready_for_applications: bool


@dataclass(frozen=True)
class ResumeOutputDTO:
    id: str
    version: int
    raw_text: str
    completeness: float
    created_at: str
