from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database.connection import get_db_session
from core.database.models import ResumeProfile
from core.resume_engine import resume_engine
from core.template_engine import template_engine

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

@router.get("/profile")
async def get_master_profile(db: AsyncSession = Depends(get_db_session)):
    stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

@router.post("/tailor")
async def tailor_resume(payload: dict):
    bullets = payload.get("bullets", [])
    jd = payload.get("job_description", "")

    if not bullets or not jd:
        raise HTTPException(status_code=400, detail="Bullets and JD are required.")

    return await resume_engine.tailor_bullets(bullets, jd)

@router.post("/export")
async def export_resume(payload: dict, db: AsyncSession = Depends(get_db_session)):
    template_id = payload.get("template_id", "classic_ats")
    file_format = payload.get("format", "pdf") # pdf or docx

    # Get master profile
    stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="No resume profile found. Create one first.")

    # Convert ORM to dict for engine
    profile_dict = {
        "full_name": profile.full_name,
        "email": profile.email,
        "phone": profile.phone,
        "location": profile.location,
        "work_history": profile.work_history
    }

    if file_format == "docx":
        output_path = f"export_{profile.id}.docx"
        template_engine.export_docx(profile_dict, output_path)
        return {"success": True, "download_url": f"/api/resumes/download/{output_path}"}

    return {"success": True, "data": template_engine.render_to_html(profile_dict, template_id)}
