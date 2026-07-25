from fastapi import APIRouter, Depends

from core.dependencies import get_task_engine
from core.schemas.api_payloads import OutreachRequest
from core.task_engine import TaskEngine

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


@router.post("")
async def generate_outreach(
    request: OutreachRequest, engine: TaskEngine = Depends(get_task_engine)
):
    return await engine.generate_outreach(request.target_role, request.company_name)
