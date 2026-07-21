from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from task_engine import TaskEngine
import os

router = APIRouter(prefix="/api/ats", tags=["ats"])

@router.post("/match")
async def match_ats(payload: dict, db: AsyncSession = Depends(get_db_session)):
    engine = TaskEngine(db)
    result = await engine.analyze_ats_fit(
        payload.get("resume_text", ""),
        payload.get("job_description", "")
    )
    return result

@router.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...), db: AsyncSession = Depends(get_db_session)):
    # Save temp file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    engine = TaskEngine(db)
    result = await engine.parse_resume_pdf(temp_path)

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return result
