from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from core.database.models import ResumeProfile
from core.dependencies import get_job_service
from core.resume_engine import resume_engine
from core.schemas.api_payloads import ResumeExportRequest
from core.template_engine import template_engine


class TailorRequest(BaseModel):
    bullets: List[str] = Field(default_factory=list)
    job_description: Optional[str] = Field("", alias="jd")
    target_role: Optional[str] = None
    job_id: Optional[int] = None

    class Config:
        populate_by_name = True


router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.get("/profile")
async def get_master_profile(job_service: any = Depends(get_job_service)):
    db = job_service.session
    stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.post("/tailor")
async def tailor_resume(request: TailorRequest):
    if not request.bullets:
        return {"data": [], "message": "No bullets provided to tailor."}

    # Use provided JD or a default search based on target_role if JD is missing
    jd_context = (
        request.job_description
        or f"Position: {request.target_role or 'Software Engineer'}"
    )

    return await resume_engine.tailor_bullets(request.bullets, jd_context)


@router.post("/export")
async def export_resume(
    request: ResumeExportRequest, job_service: any = Depends(get_job_service)
):
    db = job_service.session
    template_id = request.template_id
    file_format = request.format  # pdf or docx

    # Get master profile
    stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404, detail="No resume profile found. Create one first."
        )

    # Convert ORM to dict for engine
    profile_dict = {
        "full_name": profile.full_name,
        "email": profile.email,
        "phone": profile.phone,
        "location": profile.location,
        "work_history": profile.work_history,
    }

    if file_format == "docx":
        output_path = f"export_{profile.id}.docx"
        template_engine.export_docx(profile_dict, output_path)
        return {"success": True, "download_url": f"/api/resumes/download/{output_path}"}

    return {
        "success": True,
        "data": template_engine.render_to_html(profile_dict, template_id),
    }
