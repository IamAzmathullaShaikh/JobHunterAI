import os

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_task_engine
from core.schemas.api_payloads import MatchRequest
from core.task_engine import TaskEngine

router = APIRouter(prefix="/api/ats", tags=["ats"])


@router.post("/match")
async def match_ats(
    request: MatchRequest, engine: TaskEngine = Depends(get_task_engine)
):
    result = await engine.analyze_ats_fit(request.resume_text, request.job_description)
    return result


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
