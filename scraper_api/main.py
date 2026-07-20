"""
FastAPI entry point – exposes /scrape, /analyse, /jobs/{id}/star,
/autofill/{job_id}, and a health / metrics endpoint.
"""
import os
import hashlib
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Path, status, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# ---- Local imports ----------------------------------------------------
from jobhunterai_core.database.models import (
    JobListing,
    AIAnalysis,
    RawJob,
    LLMCache,
    ResumeVersion,
)
from jobhunterai_core.database.connection import AsyncSessionLocal
from jobhunterai_core.services.job_service import JobService
from jobhunterai_core.ai.resume_parser import ResumeParser
from jobhunterai_core.ai.matcher import Matcher

# ----------------------------------------------------------------------
# App & basic middleware
# ----------------------------------------------------------------------
app = FastAPI(title="JobHunterAI Scraper & Matcher API")

# Expose Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)

# ----------------------------------------------------------------------
# Configuration / security
# ----------------------------------------------------------------------
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEYS = set(
    filter(None, os.getenv("API_KEYS", "").split(","))
)  # e.g. "abc123,def456"


async def get_api_key(key: str = Security(API_KEY_HEADER)):
    if not API_KEYS or key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return key


# ----------------------------------------------------------------------
# Dependency: DB session
# ----------------------------------------------------------------------
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# ----------------------------------------------------------------------
# Pydantic models for request/response
# ----------------------------------------------------------------------
class ScrapeRequest(BaseModel):
    query: str
    location: str = "Remote"
    limit_per_site: int = 20
    job_type: str = "Full-Time"


class JobHit(BaseModel):
    title: str
    company: str
    location: str
    source: str
    url: str
    description: str
    posted_at: Optional[str] = None


class AnalyseRequest(BaseModel):
    job_id: int
    resume_text: str


class AnalyseResponse(BaseModel):
    match_score: float
    fit_summary: str
    keywords_matched: List[str]
    keywords_missing: List[str]


class StarUpdate(BaseModel):
    is_starred: bool


class AutofillResponse(BaseModel):
    status: str
    detail: Optional[str] = None


# ----------------------------------------------------------------------
# Helper: instantiate JobService per request
# ----------------------------------------------------------------------
async def get_job_service(db: AsyncSession = Depends(get_db)) -> JobService:
    return JobService(session=db)


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.post("/scrape", response_model=List[JobHit], dependencies=[Depends(get_api_key)])
async def scrape(
    req: ScrapeRequest,
    svc: JobService = Depends(get_job_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Run the 9‑engine scraper fleet, persist results (title/company JSON to the caller.
    """
    stored: List[JobListing] = await svc.discover_new_listings(
        search_query=req.query,
        location=req.location,
        limit=req.limit_per_site,
        job_type=req.job_type,
    )
    # Convert to lightweight DTO for n8n
    return [
        JobHit(
            title=j.title,
            company=j.company_name,
            location=j.location,
            source=j.source,
            url=j.url,
            description=j.description_raw or j.title,
            posted_at=j.date_posted.isoformat() if j.date_posted else None,
        )
        for j in stored
    ]


@app.post("/analyse", response_model=AnalyseResponse, dependencies=[Depends(get_api_key)])
async def analyse(
    req: AnalyseRequest,
    svc: JobService = Depends(get_job_service),
):
    """
    Run Groq resume‑job matching (with cache) for a single job.
    """
    # Fetch the job – if not found, 404
    job = await db.get(JobListing, req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Analyse – the service handles caching internally
    await svc.process_pending_analyses(req.resume_text)
    # Retrieve the analysis we just stored
    stmt = select(AIAnalysis).where(AIAnalysis.job_id == job.id)
    result = await db.execute(stmt)
    ai_row: Optional[AIAnalysis] = result.scalar_one_or_none()
    if not ai_row:
        raise HTTPException(status_code=500, detail="Analysis not persisted")
    return AnalyseResponse(
        match_score=ai_row.match_score,
        fit_summary=ai_row.fit_summary,
        keywords_matched=(
            ai_row.keywords_matched.split(",")
            if ai_row.keywords_matched
            else []
        ),
        keywords_missing=(
            ai_row.keywords_missing.split(",")
            if ai_row.keywords_missing
            else []
        ),
    )


@app.patch("/jobs/{job_id}/star", status_code=status.HTTP_200_OK, dependencies=[Depends(get_api_key)])
async def toggle_star(
    job_id: int = Path(..., gt=0),
    payload: StarUpdate = None,
    svc: JobService = Depends(get_job_service),
):
    """
    Mark a job as favourite (star) or un‑star it.
    """
    updated_job = await svc.toggle_star(job_id=job_id, star=payload.is_starred)
    return {
        "job_id": updated_job.id,
        "is_starred": updated_job.is_starred,
        "title": updated_job.title,
        "company": updated_job.company_name,
    }


@app.post("/autofill/{job_id}", response_model=AutofillResponse, dependencies=[Depends(get_api_key)])
async def autofill_apply(
    job_id: int = Path(..., gt=0),
    svc: JobService = Depends(get_job_service),
):
    """
    Placeholder for the Playwright‑based one‑click apply.
    In a real implementation you would:
        1. Load the JobListing (url, required fields).
        2. Retrieve the latest stored PDF (from ResumeVersion or JobApplication.final_resume_used).
        3. Launch headless Chromium, fill known selectors, upload PDF, submit.
    For now we simply return success – replace the body with your Playwright logic.
    """
    # For demo purposes we just acknowledge the request.
    return AutofillResponse(status="acknowledged", detail="Implement Playwright logic here")


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z"}
