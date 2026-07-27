"""
SQLAlchemy models for JobHunterAI – extended with all requested columns.
"""

import enum
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import (JSON, Boolean, DateTime, Enum, Float, ForeignKey,
                        Index, Integer, String, Text, UniqueConstraint)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ----------------------------------------------------------------------
# Base
# ----------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------
class ApplicationStatus(str, enum.Enum):
    WISHLIST = "Wishlist"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFERED = "Offered"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


# ----------------------------------------------------------------------
# Core tables
# ----------------------------------------------------------------------
class JobListing(Base):
    __tablename__ = "job_listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Optional multi-tenant identifier – set to NULL for single-user mode
    user_id: Mapped[Optional[UUID]] = mapped_column(
        String(36), nullable=True, index=True
    )

    job_id_raw: Mapped[str] = mapped_column(
        String(100), unique=True, index=True
    )  # external site ID
    title: Mapped[str] = mapped_column(String(255), index=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str] = mapped_column(String(255))
    work_place_type: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # Remote, Hybrid, Onsite
    job_type: Mapped[str] = mapped_column(
        String(50), default="Full-Time", server_default="Full-Time"
    )

    source: Mapped[str] = mapped_column(String(50))  # LinkedIn, Indeed, etc.
    url: Mapped[str] = mapped_column(Text)

    description_raw: Mapped[str] = mapped_column(Text)
    description_clean: Mapped[Optional[str]] = mapped_column(Text)

    # ---- Enrichment Fields ----
    required_skills: Mapped[Optional[list]] = mapped_column(JSON)
    seniority: Mapped[Optional[str]] = mapped_column(String(50))
    technologies: Mapped[Optional[list]] = mapped_column(JSON)
    benefits: Mapped[Optional[list]] = mapped_column(JSON)

    # ---- Salary fields (populated by scrapers) ----
    salary_min: Mapped[Optional[float]] = mapped_column(Float)
    salary_max: Mapped[Optional[float]] = mapped_column(Float)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")
    salary_raw: Mapped[Optional[str]] = mapped_column(
        Text
    )  # keep original string for audit

    # ---- Miscellaneous flags ----
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_suspicious: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # dark-pattern detector placeholder

    # Timestamps
    date_posted: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    date_scraped: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    ai_analysis: Mapped[Optional["AIAnalysis"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    application: Mapped[Optional["JobApplication"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    resume_versions: Mapped[List["ResumeVersion"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_joblistings_user_status", "user_id", "id"
        ),  # for multi-tenant queries
    )


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("job_listings.id", ondelete="CASCADE"), unique=True
    )

    match_score: Mapped[float] = mapped_column(Float)  # 0-100
    readability_score: Mapped[float] = mapped_column(Float, default=0.0)
    action_verb_score: Mapped[float] = mapped_column(Float, default=0.0)
    formatting_score: Mapped[float] = mapped_column(Float, default=0.0)
    quantification_score: Mapped[float] = mapped_column(Float, default=0.0)

    fit_summary: Mapped[str] = mapped_column(Text)
    keywords_matched: Mapped[Optional[list]] = mapped_column(JSON)
    keywords_missing: Mapped[Optional[list]] = mapped_column(JSON)
    detailed_recommendations: Mapped[Optional[dict]] = mapped_column(JSON)

    # Optional storage of generated artefacts
    suggested_resume_path: Mapped[Optional[str]] = mapped_column(String(500))
    suggested_cover_letter_path: Mapped[Optional[str]] = mapped_column(String(500))

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    job: Mapped["JobListing"] = relationship(back_populates="ai_analysis")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(String(36), nullable=True, index=True)
    job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("job_listings.id", ondelete="SET NULL"), unique=True, nullable=True
    )

    # Manual entry fields for Wishlist/Tracking
    job_title: Mapped[str] = mapped_column(String(255))
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    platform: Mapped[str] = mapped_column(
        String(50), default="Manual"
    )  # LinkedIn, Indeed, etc.
    job_url: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(255), default="Remote")
    salary_range: Mapped[Optional[str]] = mapped_column(String(100))
    match_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Manual Tracking
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1-3
    tags: Mapped[Optional[list]] = mapped_column(JSON)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.WISHLIST
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)

    recruiter_name: Mapped[Optional[str]] = mapped_column(String(255))
    recruiter_email: Mapped[Optional[str]] = mapped_column(String(255))

    applied_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    date_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Which concrete file was actually sent out
    final_res_used: Mapped[Optional[str]] = mapped_column(String(500))
    final_cover_used: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    job: Mapped[Optional["JobListing"]] = relationship(back_populates="application")


# ----------------------------------------------------------------------
# Auxiliary tables
# ----------------------------------------------------------------------
class RawJob(Base):
    """Store the *exact* JSON payload each scraper returned – audit / replay."""

    __tablename__ = "raw_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Which scraper produced it (linkedin, indeed, naukri, …)
    source: Mapped[str] = mapped_column(String(50), index=False)
    # The full JSON blob as text – keep it tiny for now; can be swapped for JSONB later
    raw_json: Mapped[str] = mapped_column(Text, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    __table_args__ = (Index("ix_rawjobs_source_fetched", "source", "fetched_at"),)


class LLMCache(Base):
    """Cache for the expensive Groq resume-parse call."""

    __tablename__ = "llm_cache"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # SHA-256 hex of the raw resume text
    hash: Mapped[str] = mapped_column(String(64), unique=True, index=False)
    # The parsed payload (same shape as ResumeParserOutput) stored as JSONB
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class SkillRecommendation(Base):
    """Output of the nightly skill-gap job."""

    __tablename__ = "skill_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        String(36), nullable=True, index=True
    )
    suggested_skill: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-1 relevance
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ResumeVersion(Base):
    """Allows A/B testing of multiple tailored PDFs per job."""

    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("job_listings.id", ondelete="CASCADE")
    )
    version_label: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g. "gemini_v1"
    # Store the PDF either as a base64 string or a URL to object storage.
    # For simplicity we keep a BASE64 string here (bytea would also work).
    pdf_base64: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    # Outcome when the user actually sent this version (filled manually or via email parser)
    outcome: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # NULL / INTERVIEW / OFFER / REJECTED

    # Relationships
    job: Mapped["JobListing"] = relationship(back_populates="resume_versions")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    total_experience_years: Mapped[Optional[float]] = mapped_column(Float)
    education: Mapped[Optional[list]] = mapped_column(JSON)
    key_skills: Mapped[Optional[list]] = mapped_column(JSON)
    recommended_search_queries: Mapped[Optional[list]] = mapped_column(JSON)
    experience_highlights: Mapped[Optional[list]] = mapped_column(JSON)
    raw_resume_text: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class CompanySnapshot(Base):
    """Sentiment / reputation data scraped from Glassdoor/Indeed reviews."""

    __tablename__ = "company_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(255), unique=True)
    sentiment_score: Mapped[float] = mapped_column(Float)  # 0.0-1.0 (higher = better)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ----------------------------------------------------------------------
# Telemetry and History
# ----------------------------------------------------------------------


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(
        String(100), index=True
    )  # e.g., "ai_call", "scraper_run", "db_init"
    source: Mapped[str] = mapped_column(
        String(50)
    )  # e.g., "groq_ai", "gemini_ai", "local_engine"
    latency_ms: Mapped[int] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean)
    details: Mapped[Optional[dict]] = mapped_column(
        JSON
    )  # e.g., circuit breaker state, error message
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class MatchHistory(Base):
    __tablename__ = "match_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=True
    )
    match_score: Mapped[float] = mapped_column(Float)
    readability_score: Mapped[float] = mapped_column(Float, default=0.0)
    action_verb_score: Mapped[float] = mapped_column(Float, default=0.0)
    formatting_score: Mapped[float] = mapped_column(Float, default=0.0)
    quantification_score: Mapped[float] = mapped_column(Float, default=0.0)

    fit_summary: Mapped[str] = mapped_column(Text)
    keywords_matched: Mapped[Optional[list]] = mapped_column(JSON)
    keywords_missing: Mapped[Optional[list]] = mapped_column(JSON)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# ----------------------------------------------------------------------
# Enterprise Modules: Recruiter Leads & Detailed Profiles
# ----------------------------------------------------------------------


class RecruiterContact(Base):
    """CRM table for discovered recruiters and decision makers."""

    __tablename__ = "recruiter_contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    source: Mapped[Optional[str]] = mapped_column(String(50))
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    match_explanation: Mapped[Optional[str]] = mapped_column(Text)

    # CRM State
    status: Mapped[str] = mapped_column(
        String(50), default="Not Contacted"
    )  # Sent, Viewed, Replied, Closed
    notes: Mapped[Optional[str]] = mapped_column(Text)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class OutreachMessage(Base):
    """History of messages generated for a specific recruiter."""

    __tablename__ = "outreach_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recruiter_id: Mapped[int] = mapped_column(
        ForeignKey("recruiter_contacts.id", ondelete="CASCADE")
    )
    type: Mapped[str] = mapped_column(String(50))  # Connection, Intro, Follow-up
    content: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ResumeProfile(Base):
    """Detailed Master Profile for the Resume Builder."""

    __tablename__ = "resume_master_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    skills: Mapped[Optional[list]] = mapped_column(JSON, default=[])  # List of strings
    work_history: Mapped[Optional[list]] = mapped_column(
        JSON, default=[]
    )  # List of dicts
    education: Mapped[Optional[list]] = mapped_column(JSON, default=[])  # List of dicts
    projects: Mapped[Optional[list]] = mapped_column(JSON, default=[])  # List of dicts
    certifications: Mapped[Optional[list]] = mapped_column(
        JSON, default=[]
    )  # List of dicts
    languages: Mapped[Optional[list]] = mapped_column(JSON, default=[])  # List of dicts
    achievements: Mapped[Optional[list]] = mapped_column(
        JSON, default=[]
    )  # List of strings
    awards: Mapped[Optional[list]] = mapped_column(JSON, default=[])  # List of dicts
    publications: Mapped[Optional[list]] = mapped_column(
        JSON, default=[]
    )  # List of dicts
    volunteer: Mapped[Optional[list]] = mapped_column(JSON, default=[])  # List of dicts
    interests: Mapped[Optional[list]] = mapped_column(JSON, default=[])  # List of strings
    references: Mapped[Optional[list]] = mapped_column(JSON, default=[])  # List of dicts

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Resume(Base):
    """Editable Resume documents created by the user."""

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    template_id: Mapped[str] = mapped_column(String(50), default="classic_ats")
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    # Structured JSON matching ResumeContent schema
    content: Mapped[dict] = mapped_column(JSON)

    job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("job_listings.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to CoverLetters
    cover_letters: Mapped[List["CoverLetter"]] = relationship(
        back_populates="resume", cascade="all, delete-orphan"
    )


class SavedSearch(Base):
    """Persisted user search configurations."""

    __tablename__ = "saved_searches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    query: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    job_type: Mapped[str] = mapped_column(String(50), default="Full-Time")
    filters: Mapped[dict] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class CoverLetter(Base):
    """Targeted Cover Letter documents."""

    __tablename__ = "cover_letters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    template_id: Mapped[str] = mapped_column(String(50), default="classic_ats")
    writing_style: Mapped[str] = mapped_column(String(50), default="Professional")
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    # Structured JSON matching CoverLetterContent
    content: Mapped[dict] = mapped_column(JSON)

    resume_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True
    )
    job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("job_listings.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    resume: Mapped[Optional["Resume"]] = relationship(back_populates="cover_letters")


class InterviewSession(Base):
    """Persistent interview prep sessions."""

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    difficulty: Mapped[str] = mapped_column(String(50), default="Senior")
    status: Mapped[str] = mapped_column(String(50), default="Setup")  # Setup, In-Progress, Completed
    overall_score: Mapped[Optional[float]] = mapped_column(Float)

    resume_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True
    )
    job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("job_listings.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    questions: Mapped[List["InterviewQuestion"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class InterviewQuestion(Base):
    """Individual questions within an interview session."""

    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE")
    )
    question_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50))  # Technical, Behavioural, HR
    user_answer: Mapped[Optional[str]] = mapped_column(Text)
    feedback: Mapped[Optional[dict]] = mapped_column(JSON)  # Analysis results
    score: Mapped[Optional[float]] = mapped_column(Float)
    improved_answer: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    session: Mapped["InterviewSession"] = relationship(back_populates="questions")
