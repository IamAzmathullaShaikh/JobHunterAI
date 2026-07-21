from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.connection import get_db_session
from database.models import TelemetryLog, JobListing
from smart_router import router as smart_router
import os

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/telemetry")
async def get_telemetry(db: AsyncSession = Depends(get_db_session)):
    # 1. Check API Key health
    keys = {
        "groq": bool(os.getenv("GROQ_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY"))
    }

    # 2. Get Circuit Breaker statuses
    breakers = {
        name: {
            "state": breaker.state,
            "failures": breaker.failure_count
        } for name, breaker in smart_router.breakers.items()
    }

    # 3. DB Stats
    job_count = await db.execute(select(func.count()).select_from(JobListing))

    return {
        "keys": keys,
        "circuit_breakers": breakers,
        "db_stats": {
            "total_jobs": job_count.scalar()
        }
    }
