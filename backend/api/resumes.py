from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Resume, ResumeProfile
from core.dependencies import get_job_service
from core.resume_engine import resume_engine
from core.schemas.api_payloads import (ResumeContent, ResumeCreateRequest,
                                       ResumeExportRequest,
                                       ResumeUpdateRequest)
from core.services.job_service import JobService
from core.template_engine import template_engine


class TailorRequest(BaseModel):
    bullets: List[str] = Field(default_factory=list)
    job_description: Optional[str] = Field("", alias="jd")
    target_role: Optional[str] = None
    job_id: Optional[int] = None

    class Config:
        populate_by_name = True


router = APIRouter(prefix="/api/resumes", tags=["resumes"])


# --- Master Profile ---


@router.get("/profile")
async def get_master_profile(job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.put("/profile")
async def update_master_profile(
    profile_data: dict, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = ResumeProfile(**profile_data)
        db.add(profile)
    else:
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)
    return profile


# --- Resume Documents CRUD ---


@router.get("")
async def list_resumes(job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    stmt = select(Resume).order_by(Resume.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_resume(
    request: ResumeCreateRequest, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    new_resume = Resume(
        name=request.name,
        template_id=request.template_id,
        content=request.content.model_dump(),
        job_id=request.job_id,
    )
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)
    return new_resume


@router.get("/{resume_id}")
async def get_resume(resume_id: int, job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.put("/{resume_id}")
async def update_resume(
    resume_id: int,
    request: ResumeUpdateRequest,
    job_service: JobService = Depends(get_job_service),
):
    db = job_service.session
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if request.name is not None:
        resume.name = request.name
    if request.template_id is not None:
        resume.template_id = request.template_id
    if request.content is not None:
        resume.content = request.content.model_dump()

    await db.commit()
    await db.refresh(resume)
    return resume


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    await db.delete(resume)
    await db.commit()
    return {"success": True}


@router.post("/{resume_id}/duplicate")
async def duplicate_resume(
    resume_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    new_resume = Resume(
        name=f"{resume.name} (Copy)",
        template_id=resume.template_id,
        content=resume.content,
        job_id=resume.job_id,
        is_archived=False,
    )
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)
    return new_resume


@router.put("/{resume_id}/archive")
async def archive_resume(
    resume_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume.is_archived = True
    await db.commit()
    return {"success": True}


@router.put("/{resume_id}/restore")
async def restore_resume(
    resume_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume.is_archived = False
    await db.commit()
    return {"success": True}


# --- Intelligence & Export ---


@router.get("/download/{filename}")
async def download_resume(filename: str):
    """Serves exported resume files."""
    # Ensure it's a valid filename to prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    from fastapi.responses import FileResponse

    # Files are currently saved in the current working directory by template_engine
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        filename,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.post("/tailor")
async def tailor_resume(request: TailorRequest):
    if not request.bullets:
        return {"data": [], "message": "No bullets provided to tailor."}

    jd_context = (
        request.job_description
        or f"Position: {request.target_role or 'Software Engineer'}"
    )

    return await resume_engine.tailor_bullets(request.bullets, jd_context)


@router.post("/export")
async def export_resume_api(
    request: ResumeExportRequest,
    resume_id: Optional[int] = None,
    job_service: JobService = Depends(get_job_service),
):
    db = job_service.session
    template_id = request.template_id
    file_format = request.format  # pdf or docx

    # 1. Resolve content
    profile_dict = {}
    if request.content:
        # Use content from request (WYSIWYG preview/unsaved changes)
        profile_dict = request.content.model_dump()
    elif resume_id:
        # Use specific saved resume
        resume = await db.get(Resume, resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        profile_dict = resume.content
    else:
        # Use master profile
        stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=404, detail="No resume profile found. Create one first."
            )
        # Normalize master profile to ResumeContent shape
        profile_dict = {
            "header": {
                "name": profile.full_name,
                "email": profile.email,
                "phone": profile.phone,
                "location": profile.location,
            },
            "summary": profile.summary,
            "work_history": [
                {
                    "company": j.get("company", "Unknown"),
                    "title": j.get("title", "Role"),
                    "start_date": j.get("start_date", ""),
                    "end_date": j.get("end_date", ""),
                    "bullets": j.get("bullets", [])
                } for j in (profile.work_history or [])
            ],
            "education": profile.education or [],
            "skills": profile.skills or [],
            "projects": profile.projects or [],
            "certifications": profile.certifications or []
        }

    # 2. Handle Export Formats
    if file_format == "docx":
        output_path = f"export_{resume_id or 'preview'}.docx"
        template_engine.export_docx(profile_dict, output_path)
        return {"success": True, "download_url": f"/api/resumes/download/{output_path}"}

    if file_format == "pdf":
        output_path = f"export_{resume_id or 'preview'}.pdf"
        await template_engine.export_pdf(
            profile_dict, template_id, output_path, config=request.config
        )
        return {"success": True, "download_url": f"/api/resumes/download/{output_path}"}

    if file_format == "markdown":
        return {
            "success": True,
            "data": template_engine.render_to_markdown(profile_dict),
        }

    return {
        "success": True,
        "data": template_engine.render_to_html(
            profile_dict, template_id, config=request.config
        ),
    }
