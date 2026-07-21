from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List

from core.database.connection import get_db_session
from core.database.models import JobApplication, ApplicationStatus
from core.analytics_engine import AnalyticsEngine

router = APIRouter(prefix="/api/tracker", tags=["tracker"])

@router.get("/applications")
async def get_applications(db: AsyncSession = Depends(get_db_session)):
    stmt = select(JobApplication).order_by(JobApplication.date_updated.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/applications")
async def create_application(payload: dict, db: AsyncSession = Depends(get_db_session)):
    new_app = JobApplication(**payload)
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)
    return new_app

@router.put("/applications/{app_id}/status")
async def update_status(app_id: int, payload: dict, db: AsyncSession = Depends(get_db_session)):
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required.")

    stmt = update(JobApplication).where(JobApplication.id == app_id).values(
        status=new_status,
        date_updated=__import__("datetime").datetime.utcnow()
    )
    await db.execute(stmt)
    await db.commit()
    return {"success": True}

@router.delete("/applications/{app_id}")
async def delete_application(app_id: int, db: AsyncSession = Depends(get_db_session)):
    stmt = delete(JobApplication).where(JobApplication.id == app_id)
    await db.execute(stmt)
    await db.commit()
    return {"success": True}

@router.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db_session)):
    engine = AnalyticsEngine(db)
    return await engine.get_career_metrics()
