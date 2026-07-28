from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.analytics_engine import AnalyticsEngine
from core.database.connection import get_db_session
from core.database.models import ApplicationStatus, JobApplication
from core.dependencies import get_job_service
from core.services.job_service import JobService
from core.schemas.api_payloads import (CreateApplicationRequest,
                                       UpdateApplicationRequest)

router = APIRouter(prefix="/api/tracker", tags=["tracker"])


@router.get("/applications")
async def get_applications(job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    stmt = select(JobApplication).order_by(JobApplication.date_updated.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/applications")
async def create_application(
    request: CreateApplicationRequest,
    job_service: JobService = Depends(get_job_service),
):
    db = job_service.session
    new_app = JobApplication(**request.model_dump())
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)
    return new_app


@router.put("/applications/{app_id}/status")
async def update_status(
    app_id: int,
    request: UpdateApplicationRequest,
    job_service: JobService = Depends(get_job_service),
):
    db = job_service.session
    stmt = (
        update(JobApplication)
        .where(JobApplication.id == app_id)
        .values(status=request.status, date_updated=datetime.now(timezone.utc))
    )
    await db.execute(stmt)
    await db.commit()
    return {"success": True}


@router.post("/update")
async def update_application_card(
    request: UpdateApplicationRequest,
    job_service: JobService = Depends(get_job_service),
):
    db = job_service.session
    application = await db.get(JobApplication, request.application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update fields
    application.status = request.status
    if request.notes is not None:
        application.notes = request.notes
    if request.priority is not None:
        application.priority = request.priority
    if request.tags is not None:
        application.tags = request.tags
    if request.salary_offered is not None:
        application.salary_offered = request.salary_offered
    if request.interview_date is not None:
        application.interview_date = request.interview_date
    if request.resume_id is not None:
        application.resume_id = request.resume_id
    if request.cover_letter_id is not None:
        application.cover_letter_id = request.cover_letter_id

    application.date_updated = datetime.now(timezone.utc)

    await db.commit()
    return {"ok": True}


@router.delete("/applications/{app_id}")
async def delete_application(
    app_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    stmt = delete(JobApplication).where(JobApplication.id == app_id)
    await db.execute(stmt)
    await db.commit()
    return {"success": True}


@router.get("/analytics")
async def get_analytics(
    days: int = 30,
    job_service: JobService = Depends(get_job_service)
):
    """
    Returns unified Career Intelligence data.
    """
    engine = AnalyticsEngine(job_service.session)
    return await engine.get_comprehensive_analytics(days=days)
