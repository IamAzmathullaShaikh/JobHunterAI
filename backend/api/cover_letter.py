import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from core.database.models import CoverLetter, Resume
from core.dependencies import get_job_service, get_resume_service, get_generator_service
from core.schemas.api_payloads import (CoverLetterContent,
                                       CoverLetterCreateRequest,
                                       CoverLetterGenerateRequest,
                                       CoverLetterSectionRegenerateRequest,
                                       CoverLetterUpdateRequest,
                                       CoverLetterExportRequest)
from core.services.job_service import JobService
from core.services.resume_service import ResumeService
from core.services.generator_service import GeneratorService
from core.template_engine import template_engine

router = APIRouter(prefix="/api/cover-letter", tags=["cover-letter"])


@router.get("")
async def list_cover_letters(job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    stmt = select(CoverLetter).order_by(CoverLetter.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/generate")
async def generate_cover_letter(
    request: CoverLetterGenerateRequest,
    job_service: JobService = Depends(get_job_service),
    service: GeneratorService = Depends(get_generator_service),
):
    db = job_service.session
    resume = await db.get(Resume, request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    result = await service.generate_cover_letter_structured(
        resume_content=resume.content,
        job_description=request.job_description,
        writing_style=request.writing_style,
        company_name=request.company_name,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "AI generation failed"))

    return result


@router.post("/regenerate-section")
async def regenerate_section(
    request: CoverLetterSectionRegenerateRequest,
    job_service: JobService = Depends(get_job_service),
    service: GeneratorService = Depends(get_generator_service),
):
    db = job_service.session
    resume = await db.get(Resume, request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    result = await service.regenerate_cl_section(
        section_id=request.section_id,
        resume_content=resume.content,
        job_description=request.job_description,
        writing_style=request.writing_style,
    )

    return result


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_cover_letter(
    request: CoverLetterCreateRequest, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    content_dict = request.content.model_dump()

    # Auto-sync header from linked resume OR Master Profile if missing in content
    if not content_dict.get("header") or not content_dict["header"].get("name"):
        header_source = None
        if request.resume_id:
            resume = await db.get(Resume, request.resume_id)
            if resume:
                header_source = resume.content.get("header")

        if not header_source:
             # Fallback to master profile
             profile_stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
             profile_res = await db.execute(profile_stmt)
             profile = profile_res.scalar_one_or_none()
             if profile:
                 header_source = {
                     "name": profile.full_name,
                     "email": profile.email,
                     "phone": profile.phone,
                     "location": profile.location
                 }

        if header_source:
            content_dict["header"] = header_source

    new_cl = CoverLetter(
        name=request.name,
        template_id=request.template_id,
        content=content_dict,
        resume_id=request.resume_id,
        job_id=request.job_id,
        writing_style=request.writing_style,
    )
    db.add(new_cl)
    await db.commit()
    await db.refresh(new_cl)
    return new_cl


@router.get("/{cl_id}")
async def get_cover_letter(cl_id: int, job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    cl = await db.get(CoverLetter, cl_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return cl


@router.put("/{cl_id}")
async def update_cover_letter(
    cl_id: int,
    request: CoverLetterUpdateRequest,
    job_service: JobService = Depends(get_job_service),
):
    db = job_service.session
    cl = await db.get(CoverLetter, cl_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")

    if request.name is not None:
        cl.name = request.name
    if request.template_id is not None:
        cl.template_id = request.template_id
    if request.writing_style is not None:
        cl.writing_style = request.writing_style
    if request.content is not None:
        cl.content = request.content.model_dump()

    await db.commit()
    await db.refresh(cl)
    return cl


@router.delete("/{cl_id}")
async def delete_cover_letter(
    cl_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    cl = await db.get(CoverLetter, cl_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    await db.delete(cl)
    await db.commit()
    return {"success": True}


@router.post("/{cl_id}/duplicate")
async def duplicate_cover_letter(
    cl_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    cl = await db.get(CoverLetter, cl_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")

    new_cl = CoverLetter(
        name=f"{cl.name} (Copy)",
        template_id=cl.template_id,
        content=cl.content,
        resume_id=cl.resume_id,
        job_id=cl.job_id,
        writing_style=cl.writing_style,
    )
    db.add(new_cl)
    await db.commit()
    await db.refresh(new_cl)
    return new_cl


@router.post("/export")
async def export_cover_letter(
    request: CoverLetterExportRequest,
    job_service: JobService = Depends(get_job_service),
):
    format = request.format
    content_dict = request.content.model_dump() if request.content else {}
    template_id = request.template_id

    # Fallback to master profile if header is missing
    if not content_dict.get("header"):
        stmt = select(ResumeProfile).order_by(ResumeProfile.updated_at.desc()).limit(1)
        res = await job_service.session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            content_dict["header"] = {
                "name": profile.full_name,
                "email": profile.email,
                "phone": profile.phone,
                "location": profile.location
            }

    if not content_dict:
        raise HTTPException(status_code=400, detail="Cover letter content is required for export")

    # For previews/direct rendering
    if format == "html":
        html = template_engine.render_cover_letter_to_html(content, template_id)
        return {"success": True, "data": html}

    # PDF generation logic
    if format == "pdf":
        # Use a consistent naming scheme for the output file
        # Avoid using hash(str(content)) which can be negative or inconsistent across runs
        import hashlib
        content_hash = hashlib.md5(str(content).encode()).hexdigest()[:10]
        output_filename = f"cl_export_{content_hash}.pdf"

        try:
            await template_engine.export_pdf_cover_letter(content, template_id, output_filename)
            return {"success": True, "download_url": f"/api/resumes/download/{output_filename}"}
        except Exception as e:
            logger.error(f"CL PDF export failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate PDF.")

    if format == "markdown":
        return {"success": True, "data": template_engine.render_cover_letter_to_markdown(content)}

    return {"success": False, "error": "Format not supported"}
