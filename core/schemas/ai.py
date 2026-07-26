from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApplicationStatusDTO(str, Enum):
    WISHLIST = "Wishlist"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFERED = "Offered"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


class AIAnalysisCreate(BaseModel):
    match_score: float = Field(
        ..., ge=0.0, le=100.0, description="Algorithmic compatibility percentage score."
    )
    fit_summary: str = Field(
        ..., description="Concise analysis explaining overall target alignment context."
    )
    keywords_matched: List[str] = Field(
        default_factory=list,
        description="Target keywords directly present in user profile data.",
    )
    keywords_missing: List[str] = Field(
        default_factory=list,
        description="Critical operational missing requirement items.",
    )


class AIAnalysisDTO(AIAnalysisCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    suggested_resume_path: Optional[str] = None
    suggested_cover_letter_path: Optional[str] = None
    analyzed_at: datetime


class JobApplicationCreate(BaseModel):
    job_id: int
    status: ApplicationStatusDTO = ApplicationStatusDTO.WISHLIST
    notes: Optional[str] = None


class JobApplicationDTO(JobApplicationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_created: datetime
    date_updated: datetime
    final_resume_used: Optional[str] = None
    final_cover_letter_used: Optional[str] = None
