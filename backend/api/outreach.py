from fastapi import APIRouter, Depends

from core.dependencies import get_generator_service
from core.schemas.api_payloads import OutreachRequest
from core.services.generator_service import GeneratorService

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


@router.post("")
async def generate_outreach(
    request: OutreachRequest, service: GeneratorService = Depends(get_generator_service)
):
    return await service.generate_outreach(request.target_role, request.company_name)
