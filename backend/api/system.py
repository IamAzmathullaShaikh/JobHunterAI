from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.ai.smart_router import route as smart_router
from core.config.settings import settings
from core.database.connection import get_db_session

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/telemetry")
async def telemetry():
    """Simple telemetry check as requested."""
    return {
        "status": "ok",
        "message": "System telemetry active",
        "env": settings.ENVIRONMENT,
    }


@router.post("/test-router")
async def test_router(request: Request):
    """
    Demonstrates the true 3-tier fallback logic.
    Returns cloud result by default, local fallback when {"force_fail": true} is posted.
    """
    payload = await request.json()

    async def groq_tier(**kwargs):
        if payload.get("force_fail"):
            raise RuntimeError("Simulated Tier 1 failure")
        return {"source": "cloud", "data": "Groq result"}

    groq_tier.required_envs = ["GROQ_API_KEY"]

    async def gemini_tier(**kwargs):
        return {"source": "cloud", "data": "Gemini result"}

    gemini_tier.required_envs = ["GEMINI_API_KEY"]

    def local_tier(**kwargs):
        return {"source": "local", "data": "Local fallback result"}

    result = await smart_router(groq_tier, gemini_tier, local_tier)
    return {"ok": True, "result": result}
