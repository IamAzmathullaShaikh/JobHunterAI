import os

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_task_engine
from core.schemas.api_payloads import BulletOptimizeRequest, MatchRequest
from core.task_engine import TaskEngine

router = APIRouter(prefix="/api/ats", tags=["ats"])


@router.post("/match")
async def match_ats(
    request: MatchRequest, engine: TaskEngine = Depends(get_task_engine)
):
    result = await engine.analyze_ats_fit(request.resume_text, request.job_description)
    return result


@router.post("/optimize-bullet")
async def optimize_bullet(
    request: BulletOptimizeRequest, engine: TaskEngine = Depends(get_task_engine)
):
    # This calls the new optimize_bullet logic
    from core.ai.matcher import JobMatcher

    matcher = JobMatcher()
    return await matcher.optimize_bullet(request.bullet, request.jd)


@router.get("/history")
async def get_ats_history(
    job_id: Optional[int] = None,
    engine: TaskEngine = Depends(get_task_engine)
):
    from core.database.models import MatchHistory
    from sqlalchemy import select
    stmt = select(MatchHistory)
    if job_id:
        stmt = stmt.where(MatchHistory.job_id == job_id)
    stmt = stmt.order_by(MatchHistory.timestamp.desc())
    result = await engine.db.execute(stmt)
    return result.scalars().all()


@router.post("/parse-pdf")
async def parse_pdf(
    file: UploadFile = File(...), engine: TaskEngine = Depends(get_task_engine)
):
    # Save temp file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    result = await engine.parse_resume_pdf(temp_path)

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return result
