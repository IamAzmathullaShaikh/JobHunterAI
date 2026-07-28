from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.connection import get_db_session
from core.database.models import (AIAnalysis, ApplicationStatus,
                                  JobApplication, JobListing, SavedSearch)
from core.dependencies import get_job_service, get_resume_service
from core.schemas.api_payloads import (JobAnalysisRequest, ResumeParseRequest,
                                       SavedSearchCreate, ScrapeRequest,
                                       TrackJobRequest)
from core.schemas.job_listing import JobListingRead
from core.scraper import scrape_jobs
from core.services.job_service import JobService
from core.services.resume_service import ResumeService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/scrape")
async def scrape_jobs_api(
    request: ScrapeRequest, job_service: JobService = Depends(get_job_service)
):
    """
    Unified scrape endpoint with Tiered Routing.
    Cloud (Apify) -> Local (JobSpy).
    """
    new_jobs = await job_service.discover_new_listings(
        search_query=request.search_query,
        location=request.location,
        limit=request.limit,
        job_type=request.job_type,
    )

    return {
        "scraped_count": len(new_jobs),
        "new_count": len(new_jobs),
        "jobs": new_jobs,
    }


@router.get("")
async def get_jobs(
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None,
    company: Optional[str] = None,
    seniority: Optional[str] = None,
    mode: str = "scraped", # "scraped" or "all"
    job_service: JobService = Depends(get_job_service),
):
    # 1. Fetch Scraped Jobs
    stmt = select(JobListing)
    if search:
        stmt = stmt.where(JobListing.title.ilike(f"%{search}%"))
    if company:
        stmt = stmt.where(JobListing.company_name.ilike(f"%{company}%"))
    if seniority:
        stmt = stmt.where(JobListing.seniority == seniority)

    stmt = stmt.order_by(JobListing.date_scraped.desc()).limit(limit).offset(offset)
    result = await job_service.session.execute(stmt)
    jobs = result.scalars().all()

    if mode == "all":
        # 2. Fetch Manual Applications to merge
        from core.database.models import JobApplication
        app_stmt = select(JobApplication).where(JobApplication.job_id == None)
        app_res = await job_service.session.execute(app_stmt)
        manual_apps = app_res.scalars().all()

        # Convert manual apps to job-like structure for UI consistency
        for app in manual_apps:
            # Check if already added via search
            if not any(j.title == app.job_title and j.company_name == app.company_name for j in jobs):
                jobs.append({
                    "id": f"app-{app.id}", # Virtual ID for UI
                    "title": app.job_title,
                    "company_name": app.company_name,
                    "location": app.location,
                    "source": app.platform,
                    "url": app.job_url or "#",
                    "application": app,
                    "date_scraped": app.date_created,
                    "description_raw": app.notes or "Manual entry."
                })

    return {"jobs": jobs}


# --- Saved Searches ---


@router.get("/saved-searches")
async def list_saved_searches(job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    stmt = select(SavedSearch).order_by(SavedSearch.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/saved-searches")
async def save_search(
    request: SavedSearchCreate, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    new_search = SavedSearch(**request.model_dump())
    db.add(new_search)
    await db.commit()
    await db.refresh(new_search)
    return new_search


@router.delete("/saved-searches/{search_id}")
async def delete_saved_search(
    search_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    search = await db.get(SavedSearch, search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    await db.delete(search)
    await db.commit()
    return {"success": True}


@router.post("/search-all")
async def search_all_platforms(
    request: ScrapeRequest,
    job_service: JobService = Depends(get_job_service)
):
    results = await job_service.search_live(
        query=request.search_query,
        location=request.location,
        limit=request.limit
    )
    return {"source": "jobspy", "data": results}


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
            job_id=job.id, status=ApplicationStatus.WISHLIST, notes=""
        )
        db.add(app)
        await db.commit()
        await db.refresh(job)

    return {"job": job}


@router.post("/analyze")
async def analyze_job(
    request: JobAnalysisRequest,
    job_service: JobService = Depends(get_job_service),
    service: ResumeService = Depends(get_resume_service),
):
    db = job_service.session
    stmt = select(JobListing).where(JobListing.id == request.job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # Use the decoupled ResumeService
    analysis_result = await service.analyze_fit(
        request.resume_text, job.description_raw or job.title
    )

    if not analysis_result["success"]:
        raise HTTPException(
            status_code=500, detail=analysis_result.get("error", "AI Analysis failed")
        )

    # Save to AIAnalysis table for this job
    data = analysis_result["data"]
    if job.ai_analysis:
        job.ai_analysis.match_score = data.get("match_score", 0)
        job.ai_analysis.readability_score = data.get("readability_score", 0)
        job.ai_analysis.action_verb_score = data.get("action_verb_score", 0)
        job.ai_analysis.formatting_score = data.get("formatting_score", 0)
        job.ai_analysis.quantification_score = data.get("quantification_score", 0)
        job.ai_analysis.fit_summary = data.get("fit_summary", "")
        job.ai_analysis.keywords_matched = data.get("keywords_matched", [])
        job.ai_analysis.keywords_missing = data.get("keywords_missing", [])
        job.ai_analysis.detailed_recommendations = data.get("detailed_recommendations", {})
    else:
        new_analysis = AIAnalysis(
            job_id=job.id,
            match_score=data.get("match_score", 0),
            readability_score=data.get("readability_score", 0),
            action_verb_score=data.get("action_verb_score", 0),
            formatting_score=data.get("formatting_score", 0),
            quantification_score=data.get("quantification_score", 0),
            fit_summary=data.get("fit_summary", ""),
            keywords_matched=data.get("keywords_matched", []),
            keywords_missing=data.get("keywords_missing", []),
            detailed_recommendations=data.get("detailed_recommendations", {}),
        )
        db.add(new_analysis)

    await db.commit()
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
