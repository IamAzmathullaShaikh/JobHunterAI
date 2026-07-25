from typing import List, Optional

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    search_query: str = Field(..., alias="query")
    location: str = "Remote"
    limit: int = 10
    job_type: str = "Full-Time"
    candidate_context: Optional[str] = None

    class Config:
        populate_by_name = True


class ResumeParseRequest(BaseModel):
    text: Optional[str] = None
    fileBase64: Optional[str] = None
    fileType: Optional[str] = None
    fileName: Optional[str] = None


class JobAnalysisRequest(BaseModel):
    job_id: int
    resume_text: str


class MatchRequest(BaseModel):
    resume_text: str
    job_description: str


class InterviewFeedbackRequest(BaseModel):
    question: str
    response: str


class RecruiterSearchRequest(BaseModel):
    company_name: str
    department: str = "Engineering"


class ResumeExportRequest(BaseModel):
    format: str = "pdf"
    template_id: str = "classic_ats"


class OutreachRequest(BaseModel):
    target_role: str
    company_name: str


class TrackJobRequest(BaseModel):
    job_id: int


class CreateApplicationRequest(BaseModel):
    job_id: Optional[int] = None
    job_title: str
    company_name: str
    platform: str = "Manual"
    job_url: Optional[str] = None
    location: str = "Remote"
    status: str = "Identified"
    notes: Optional[str] = ""


class UpdateApplicationRequest(BaseModel):
    application_id: int
    status: str
    notes: Optional[str] = ""
