from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database.connection import get_db_session
from core.database.models import TelemetryLog, JobListing
from core.ai.smart_router import route as smart_router
import os

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/telemetry")
async def telemetry():
    """Simple telemetry check as requested."""
    return {"status": "ok", "message": "System telemetry active"}

@router.post("/test-router")
async def test_router(request: Request):
    """
    Demonstrates the 3-tier fallback logic.
    Returns cloud result by default, local fallback when {"force_fail": true} is posted.
    """
    payload = await request.json()

    def primary_fn(data):
        if data.get("force_fail"):
            raise RuntimeError("Simulated cloud failure")
        return {"source": "cloud", "data": "Cloud result"}

    # Mark primary_fn with required envs for the router to check
    primary_fn.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

    def fallback_fn(data):
        return {"source": "local", "data": "Local fallback result"}

    result = await smart_router(primary_fn, fallback_fn, payload)
    return {"ok": True, "result": result}
