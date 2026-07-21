from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class AIAnalysisBase(BaseModel):
    match_score: float = Field(..., ge=0.0, le=100.0, description="Fit score percentage")
    fit_summary: str = Field(..., description="Summary breakdown of candidate alignment")
    keywords_matched: List[str] = Field(default_factory=list)
    keywords_missing: List[str] = Field(default_factory=list)
    suggested_resume_path: Optional[str] = None
    suggested_cover_letter_path: Optional[str] = None

class AIAnalysisCreate(AIAnalysisBase):
    pass

class AIAnalysisRead(AIAnalysisBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    analyzed_at: datetime