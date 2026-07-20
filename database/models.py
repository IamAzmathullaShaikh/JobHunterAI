"""
SQLAlchemy models for JobHunterAI – extended with all requested columns.
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import String, Text, DateTime, Float, Boolean, ForeignKey, Index, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

# ----------------------------------------------------------------------
# Base
# ----------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------
class ApplicationStatus(str, enum.Enum):
    IDENTIFIED = "Identified"
    AI_READY = "AI Ready"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


# ----------------------------------------------------------------------
# Core tables
# ----------------------------------------------------------------------
class JobListing(Base):
    __tablename__ = "job_listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Optional multi-tenant identifier – set to NULL for single-user mode
    user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)

    job_id_raw: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # external site ID
    title: Mapped[str] = mapped_column(String(255), index=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str] = mapped_column(String(255))
    work_place_type: Mapped[Optional[str]] = mapped_column(String(50))  # Remote, Hybrid, Onsite
    job_type: Mapped[str] = mapped_column(String(50), default="Full-Time", server_default="Full-Time")

    source: Mapped[str] = mapped_column(String(50))  # LinkedIn, Indeed, etc.
    url: Mapped[str] = mapped_column(Text)

    description_raw: Mapped[str] = mapped_column(Text)
    description_clean: Mapped[Optional[str]] = mapped_column(Text)

    # ---- Salary fields (populated by scrapers) ----
    salary_min: Mapped[Optional[float]] = mapped_column(Float)
    salary_max: Mapped[Optional[float]] = mapped_column(Float)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")
    salary_raw: Mapped[Optional[str]] = mapped_column(Text)          # keep original string for audit

    # ---- Miscellaneous flags ----
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)   # dark-pattern detector placeholder

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
        Index("ix_joblistings_user_status", "user_id", "id"),  # for multi-tenant queries
    )


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_listings.id", ondelete="CASCADE"), unique=True)

    match_score: Mapped[float] = mapped_column(Float)               # 0-100
    fit_summary: Mapped[str] = mapped_column(Text)
    keywords_matched: Mapped[str] = mapped_column(Text)            # CSV or JSON – keep simple CSV for now
    keywords_missing: Mapped[str] = mapped_column(Text)

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
    job_id: Mapped[int] = mapped_column(ForeignKey("job_listings.id", ondelete="CASCADE"), unique=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        sa_enum=ApplicationStatus, default=ApplicationStatus.IDENTIFIED
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)

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
    job: Mapped["JobListing"] = relationship(back_populates="application")


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
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class SkillRecommendation(Base):
    """Output of the nightly skill-gap job."""
    __tablename__ = "skill_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    suggested_skill: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)   # 0-1 relevance
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ResumeVersion(Base):
    """Allows A/B testing of multiple tailored PDFs per job."""
    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_listings.id", ondelete="CASCADE"))
    version_label: Mapped[str] = mapped_column(String(50), nullable=False)   # e.g. "gemini_v1"
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


class CompanySnapshot(Base):
    """Sentiment / reputation data scraped from Glassdoor/Indeed reviews."""
    __tablename__ = "company_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(255), unique=True)
    sentiment_score: Mapped[float] = mapped_column(Float)   # 0.0-1.0 (higher = better)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


# ----------------------------------------------------------------------
# Vector similarity placeholder (pgvector) – add column later if you enable the extension
# ----------------------------------------------------------------------
# If you run `CREATE EXTENSION IF NOT EXISTS vector;` in Postgres, uncomment:
# class JobListing(Base):
#     __tablename__ = "job_listings"
#     ...
#     embedding: Mapped[Optional[list[float]]] = mapped_column(
#         ARRAY(Float),  # simple fallback; replace with Vector(384) when pgvector is installed
#         nullable=True
#     )
