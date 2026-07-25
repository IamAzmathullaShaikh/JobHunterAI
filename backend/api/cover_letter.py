from fastapi import APIRouter, Depends

from core.dependencies import get_task_engine
from core.schemas.api_payloads import MatchRequest
from core.task_engine import TaskEngine

router = APIRouter(prefix="/api/cover-letter", tags=["cover-letter"])


@router.post("/generate")
async def generate_cover_letter(
    request: MatchRequest, engine: TaskEngine = Depends(get_task_engine)
):
    return await engine.generate_cover_letter(
        request.resume_text, request.job_description
    )
