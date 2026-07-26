from typing import List, Optional

from pydantic import BaseModel, Field

from core.database.models import ApplicationStatus


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


class BulletOptimizeRequest(BaseModel):
    bullet: str
    jd: str


class PrepRequest(BaseModel):
    job_description: str


class RecruiterSearchRequest(BaseModel):
    company_name: str
    department: str = "Engineering"
    resume_text: Optional[str] = None
    job_title: Optional[str] = None
    user_name: Optional[str] = None
    seniority: Optional[str] = None
    industry: Optional[str] = None


class RecruiterContactCreate(BaseModel):
    name: str
    title: str
    company: str
    department: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None
    confidence_score: float = 0.0


class RecruiterStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


class OutreachGenerateRequest(BaseModel):
    recruiter_id: int
    resume_id: int
    job_id: Optional[int] = None
    message_type: str = "Intro"  # Connection, Intro, Follow-up


class ResumeExportRequest(BaseModel):
    format: str = "pdf"
    template_id: str = "classic_ats"
    content: Optional["ResumeContent"] = None
    config: Optional[dict] = None


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
    status: str = ApplicationStatus.WISHLIST.value
    notes: Optional[str] = ""
    priority: int = 1
    tags: List[str] = Field(default_factory=list)


class UpdateApplicationRequest(BaseModel):
    application_id: Optional[int] = None
    status: str
    notes: Optional[str] = ""
    priority: Optional[int] = None
    tags: Optional[List[str]] = None


class SavedSearchCreate(BaseModel):
    name: str
    query: str
    location: str = "Remote"
    job_type: str = "Full-Time"
    filters: dict = Field(default_factory=dict)


# --- Resume System V2 ---


class ResumeContent(BaseModel):
    header: dict = Field(default_factory=dict)
    summary: str = ""
    work_history: List[dict] = Field(default_factory=list)
    education: List[dict] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[dict] = Field(default_factory=list)
    certifications: List[dict] = Field(default_factory=list)
    languages: List[dict] = Field(default_factory=list)
    awards: List[dict] = Field(default_factory=list)
    publications: List[dict] = Field(default_factory=list)
    volunteer: List[dict] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    references: List[dict] = Field(default_factory=list)
    custom_sections: List[dict] = Field(default_factory=list)


class ResumeCreateRequest(BaseModel):
    name: str
    template_id: str = "classic_ats"
    content: ResumeContent
    job_id: Optional[int] = None


class ResumeUpdateRequest(BaseModel):
    name: Optional[str] = None
    template_id: Optional[str] = None
    content: Optional[ResumeContent] = None


# --- Cover Letter System ---


class CoverLetterContent(BaseModel):
    header: dict = Field(default_factory=dict)
    salutation: str = "Dear Hiring Manager,"
    opening: str = ""
    why_us: str = ""
    experience_highlight: str = ""
    closing: str = ""
    sign_off: str = "Best regards,"


class CoverLetterGenerateRequest(BaseModel):
    resume_id: int
    job_description: str
    company_name: Optional[str] = None
    writing_style: str = "Professional"


class CoverLetterSectionRegenerateRequest(BaseModel):
    section_id: str  # opening, why_us, experience_highlight, closing
    current_content: str
    resume_id: int
    job_description: str
    writing_style: str = "Professional"


class CoverLetterCreateRequest(BaseModel):
    name: str
    template_id: str = "classic_ats"
    content: CoverLetterContent
    resume_id: Optional[int] = None
    job_id: Optional[int] = None
    writing_style: str = "Professional"


class CoverLetterUpdateRequest(BaseModel):
    name: Optional[str] = None
    template_id: Optional[str] = None
    content: Optional[CoverLetterContent] = None
    writing_style: Optional[str] = None


class CoverLetterExportRequest(BaseModel):
    format: str = "pdf"
    template_id: str = "classic_ats"
    content: Optional[CoverLetterContent] = None


# --- Interview System ---


class InterviewSessionCreateRequest(BaseModel):
    name: str
    resume_id: int
    job_id: Optional[int] = None
    job_description: Optional[str] = None
    difficulty: str = "Senior"


class AnswerSubmissionRequest(BaseModel):
    user_answer: str


class SessionExportRequest(BaseModel):
    format: str = "pdf"
