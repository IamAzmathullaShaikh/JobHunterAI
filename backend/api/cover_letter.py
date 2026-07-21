from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from task_engine import TaskEngine

router = APIRouter(prefix="/api/cover-letter", tags=["cover-letter"])

@router.post("/generate")
async def generate_cover_letter(payload: dict, db: AsyncSession = Depends(get_db_session)):
    engine = TaskEngine(db)
    return await engine.generate_cover_letter(
        payload.get("resume_text", ""),
        payload.get("job_details", "")
    )
