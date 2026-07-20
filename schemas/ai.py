from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class ApplicationStatusDTO(str, Enum):
    IDENTIFIED = "Identified"
    AI_READY = "AI Ready"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"

class AIAnalysisCreate(BaseModel):
    match_score: float = Field(..., ge=0.0, le=100.0, description="Algorithmic compatibility percentage score.")
    fit_summary: str = Field(..., description="Concise analysis explaining overall target alignment context.")
    keywords_matched: List[str] = Field(default_factory=list, description="Target keywords directly present in user profile data.")
    keywords_missing: List[str] = Field(default_factory=list, description="Critical operational missing requirement items.")

class AIAnalysisDTO(AIAnalysisCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    job_id: int
    suggested_resume_path: Optional[str] = None
    suggested_cover_letter_path: Optional[str] = None
    analyzed_at: datetime

class JobApplicationCreate(BaseModel):
    job_id: int
    status: ApplicationStatusDTO = ApplicationStatusDTO.IDENTIFIED
    notes: Optional[str] = None

class JobApplicationDTO(JobApplicationCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date_created: datetime
    date_updated: datetime
    final_resume_used: Optional[str] = None
    final_cover_letter_used: Optional[str] = None