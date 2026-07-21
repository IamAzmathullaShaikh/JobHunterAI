from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database.connection import get_db_session
from database.models import JobListing, ApplicationStatus, JobApplication, AIAnalysis
from services.job_service import JobService
from schemas.job_listing import JobListingRead

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/")
async def get_jobs(
    db: AsyncSession = Depends(get_db_session),
    limit: int = 100,
    offset: int = 0
):
    stmt = select(JobListing).order_by(JobListing.date_scraped.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return {"jobs": jobs}

@router.post("/scrape")
async def scrape_jobs(payload: dict, db: AsyncSession = Depends(get_db_session)):
    query = payload.get("search_query")
    location = payload.get("location", "Remote")
    limit = payload.get("limit", 10)
    job_type = payload.get("job_type", "Full-Time")

    if not query:
        raise HTTPException(status_code=400, detail="Search query is required.")

    service = JobService(db)
    new_jobs = await service.discover_new_listings(
        search_query=query,
        location=location,
        limit=limit,
        job_type=job_type
    )

    return {
        "scraped_count": len(new_jobs),
        "new_count": len(new_jobs),
        "jobs": new_jobs
    }

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

    service = JobService(db)
    # Re-using the logic from JobService but for a specific job
    # We can either update JobService to handle single job or do it here
    # For now, let's call the matcher directly
    from ai.matcher import JobMatcher
    matcher = JobMatcher()

    stmt = select(JobListing).where(JobListing.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    analysis = await matcher.analyze_fit(job.description_raw or job.title, resume_text)

    ai_record = AIAnalysis(
        job_id=job.id,
        match_score=analysis.match_score,
        fit_summary=analysis.fit_summary,
        keywords_matched=",".join(analysis.keywords_matched),
        keywords_missing=",".join(analysis.keywords_missing)
    )
    db.add(ai_record)
    await db.commit()
    await db.refresh(job)

    return {"job": job}
