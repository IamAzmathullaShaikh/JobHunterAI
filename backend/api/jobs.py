from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.connection import get_db_session
from core.database.models import (AIAnalysis, ApplicationStatus,
                                  JobApplication, JobListing)
from core.dependencies import get_job_service, get_task_engine
from core.schemas.api_payloads import (JobAnalysisRequest, ResumeParseRequest,
                                       ScrapeRequest, TrackJobRequest)
from core.schemas.job_listing import JobListingRead
from core.scraper import scrape_jobs
from core.services.job_service import JobService
from core.task_engine import TaskEngine

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/scrape")
async def scrape_jobs_api(
    request: ScrapeRequest, job_service: JobService = Depends(get_job_service)
):
    """
    Unified scrape endpoint with Tiered Routing.
    Cloud (Apify) -> Local (JobSpy).
    """
    # Map back to dict if scrape_jobs expects it, or update scrape_jobs
    payload = request.model_dump(by_alias=True)
    results = await scrape_jobs(payload)

    return results


@router.get("")
async def get_jobs(
    limit: int = 100,
    offset: int = 0,
    job_service: JobService = Depends(get_job_service),
):
    stmt = (
        select(JobListing)
        .order_by(JobListing.date_scraped.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await job_service.session.execute(stmt)
    jobs = result.scalars().all()
    return {"jobs": jobs}


@router.post("/search-all")
async def search_all_platforms(request: ScrapeRequest):
    payload = request.model_dump(by_alias=True)
    from core.scraper_engine import scraper_engine

    results = await scraper_engine.search_all(
        payload.get("search_query"),
        payload.get("location"),
        payload.get("limit"),
        [],  # platforms
    )
    return results


@router.post("/track")
async def track_job(
    request: TrackJobRequest, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    stmt = select(JobListing).where(JobListing.id == request.job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if not job.application:
        app = JobApplication(
            job_id=job.id, status=ApplicationStatus.IDENTIFIED, notes=""
        )
        db.add(app)
        await db.commit()
        await db.refresh(job)

    return {"job": job}


@router.post("/analyze")
async def analyze_job(
    request: JobAnalysisRequest,
    job_service: JobService = Depends(get_job_service),
    engine: TaskEngine = Depends(get_task_engine),
):
    db = job_service.session
    stmt = select(JobListing).where(JobListing.id == request.job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # Use the unified TaskEngine which includes Caching, Truncation, and Smart Routing
    analysis_result = await engine.analyze_ats_fit(
        request.resume_text, job.description_raw or job.title
    )

    if not analysis_result["success"]:
        raise HTTPException(
            status_code=500, detail=analysis_result.get("error", "AI Analysis failed")
        )

    # Reload job to get updated relationship if needed, though TaskEngine saves to DB
    await db.refresh(job)
    return {
        "job": job,
        "meta": {
            "source": analysis_result["source"],
            "latency": analysis_result["latency_ms"],
        },
    }


@router.post("/analyze-pending")
async def analyze_pending_jobs(
    request: ResumeParseRequest, job_service: JobService = Depends(get_job_service)
):
    resume_text = request.text
    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text is required.")
    count = await job_service.process_pending_analyses(resume_text)

    return {"count": count, "message": f"Successfully analyzed {count} pending jobs."}
