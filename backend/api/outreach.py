from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from task_engine import TaskEngine

router = APIRouter(prefix="/api/outreach", tags=["outreach"])

@router.post("/message")
async def generate_outreach(payload: dict, db: AsyncSession = Depends(get_db_session)):
    engine = TaskEngine(db)
    return await engine.generate_outreach(
        payload.get("target_role", ""),
        payload.get("company", "")
    )
