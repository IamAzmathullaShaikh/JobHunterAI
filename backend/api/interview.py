from fastapi import APIRouter, Depends

from core.dependencies import get_task_engine
from core.schemas.api_payloads import InterviewFeedbackRequest, MatchRequest
from core.task_engine import TaskEngine

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/prep")
async def prep_interview(
    request: MatchRequest, engine: TaskEngine = Depends(get_task_engine)
):
    return await engine.prepare_interview(request.job_description)


@router.post("/feedback")
async def star_feedback(
    request: InterviewFeedbackRequest, engine: TaskEngine = Depends(get_task_engine)
):
    return await engine.provide_star_feedback(request.question, request.response)
