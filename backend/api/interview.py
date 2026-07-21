from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from task_engine import TaskEngine

router = APIRouter(prefix="/api/interview", tags=["interview"])

@router.post("/prep")
async def prep_interview(payload: dict, db: AsyncSession = Depends(get_db_session)):
    engine = TaskEngine(db)
    return await engine.prepare_interview(payload.get("job_description", ""))
