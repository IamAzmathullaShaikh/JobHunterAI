from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.analytics_engine import AnalyticsEngine
from core.database.connection import get_db_session
from core.database.models import ApplicationStatus, JobApplication
from core.dependencies import get_job_service
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
        .values(
            status=request.status, date_updated=__import__("datetime").datetime.utcnow()
        )
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
    stmt = (
        update(JobApplication)
        .where(JobApplication.id == request.application_id)
        .values(
            status=request.status,
            notes=request.notes,
            date_updated=__import__("datetime").datetime.utcnow(),
        )
    )
    await db.execute(stmt)
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
async def get_analytics(job_service: JobService = Depends(get_job_service)):
    engine = AnalyticsEngine(job_service.session)
    return await engine.get_career_metrics()
