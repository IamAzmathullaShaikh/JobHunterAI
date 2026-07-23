from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from core.database.connection import get_db_session
from core.database.models import JobListing, ApplicationStatus, JobApplication, AIAnalysis
from core.services.job_service import JobService
from core.schemas.job_listing import JobListingRead

from core.scraper import scrape_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/scrape")
async def scrape_jobs_api(payload: dict, db: AsyncSession = Depends(get_db_session)):
    """
    Unified scrape endpoint with Tiered Routing.
    Cloud (Apify) -> Local (JobSpy).
    """
    results = await scrape_jobs(payload)

    # If the user expects these to be persisted to DB automatically (like the old endpoint)
    # we can add that logic here using JobService.
    if results.get("data"):
        # This part ensures the scraped jobs are deduplicated and saved to SQLite
        service = JobService(db)
        # We might need to map the results to JobListingCreate schemas if they differ
        # For now, we'll return the results directly as requested by the Tiered strategy
        pass

    return results

@router.get("")
async def get_jobs(
    db: AsyncSession = Depends(get_db_session),
    limit: int = 100,
    offset: int = 0
):
    stmt = select(JobListing).order_by(JobListing.date_scraped.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return {"jobs": jobs}

@router.post("/search-all")
async def search_all_platforms(payload: dict):
    query = payload.get("search_query")
    location = payload.get("location", "Remote")
    platforms = payload.get("platforms", [])
    limit = payload.get("limit", 20)

    if not query:
        raise HTTPException(status_code=400, detail="Search query is required.")

    from core.scraper_engine import scraper_engine
    results = await scraper_engine.search_all(query, location, limit, platforms)
    return results

@router.post("/track")
async def track_job(payload: dict, db: AsyncSession = Depends(get_db_session)):
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID is required.")

    stmt = select(JobListing).where(JobListing.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if not job.application:
        app = JobApplication(
            job_id=job.id,
            status=ApplicationStatus.IDENTIFIED,
            notes=""
        )
        db.add(app)
        await db.commit()
        await db.refresh(job)

    return {"job": job}

@router.post("/analyze")
async def analyze_job(payload: dict, db: AsyncSession = Depends(get_db_session)):
    job_id = payload.get("job_id")
    resume_text = payload.get("resume_text")

    if not job_id or not resume_text:
        raise HTTPException(status_code=400, detail="Job ID and Resume text are required.")

    stmt = select(JobListing).where(JobListing.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    from task_engine import TaskEngine
    engine = TaskEngine(db)

    # Use the unified TaskEngine which includes Caching, Truncation, and Smart Routing
    analysis_result = await engine.analyze_ats_fit(resume_text, job.description_raw or job.title)

    if not analysis_result["success"]:
        raise HTTPException(status_code=500, detail=analysis_result.get("error", "AI Analysis failed"))

    # Reload job to get updated relationship if needed, though TaskEngine saves to DB
    await db.refresh(job)
    return {"job": job, "meta": {"source": analysis_result["source"], "latency": analysis_result["latency_ms"]}}

@router.post("/analyze-pending")
async def analyze_pending_jobs(payload: dict, db: AsyncSession = Depends(get_db_session)):
    resume_text = payload.get("resume_text")
    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text is required.")

    from core.services.job_service import JobService
    service = JobService(db)
    count = await service.process_pending_analyses(resume_text)

    return {"count": count, "message": f"Successfully analyzed {count} pending jobs."}
