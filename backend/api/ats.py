import os
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_resume_service
from core.schemas.api_payloads import BulletOptimizeRequest, MatchRequest
from core.services.resume_service import ResumeService

router = APIRouter(prefix="/api/ats", tags=["ats"])


@router.post("/match")
async def match_ats(
    request: MatchRequest, service: ResumeService = Depends(get_resume_service)
):
    result = await service.analyze_fit(request.resume_text, request.job_description)
    return result


@router.post("/optimize-bullet")
async def optimize_bullet(
    request: BulletOptimizeRequest, service: ResumeService = Depends(get_resume_service)
):
    return await service.tailor_bullets([request.bullet], request.jd)


@router.get("/history")
async def get_ats_history(
    job_id: Optional[int] = None,
    service: ResumeService = Depends(get_resume_service)
):
    from core.database.models import MatchHistory
    from sqlalchemy import select
    stmt = select(MatchHistory)
    if job_id:
        stmt = stmt.where(MatchHistory.job_id == job_id)
    stmt = stmt.order_by(MatchHistory.timestamp.desc())
    result = await service.db.execute(stmt)
    return result.scalars().all()


@router.post("/parse-pdf")
async def parse_pdf(
    file: UploadFile = File(...), service: ResumeService = Depends(get_resume_service)
):
    # Save temp file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    result = await service.parse_pdf(temp_path)

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return result
