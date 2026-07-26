from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from core.database.models import RecruiterContact, Resume
from core.dependencies import get_enricher, get_job_service, get_task_engine
from core.enricher import Enricher
from core.schemas.api_payloads import (OutreachGenerateRequest,
                                       RecruiterContactCreate,
                                       RecruiterSearchRequest,
                                       RecruiterStatusUpdate)
from core.services.job_service import JobService
from core.task_engine import TaskEngine

router = APIRouter(prefix="/api/recruiters", tags=["recruiters"])


@router.post("/find")
async def find_recruiters(
    request: RecruiterSearchRequest, enricher: Enricher = Depends(get_enricher)
):
    """Discovers recruiters using live providers and ranks them."""
    company = request.company_name
    dept = request.department

    if not company:
        raise HTTPException(status_code=400, detail="Company name is required.")

    leads = await enricher.find_decision_makers(company, dept)

    # 1. Rank recruiters using AI
    resume_content = {}
    if request.resume_text:
        resume_content = {"summary": request.resume_text[:2000]}

    from core.ranking_engine import ranking_engine
    ranked_leads = await ranking_engine.rank_recruiters(
        resume_content=resume_content,
        target_department=dept,
        recruiters=leads
    )

    return ranked_leads


# --- Recruiter CRM (My Contacts) ---


@router.get("/contacts")
async def list_contacts(job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    stmt = select(RecruiterContact).order_by(RecruiterContact.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/contacts", status_code=status.HTTP_201_CREATED)
async def add_to_crm(
    request: RecruiterContactCreate, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    new_contact = RecruiterContact(**request.model_dump())
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


@router.put("/contacts/{contact_id}")
async def update_contact(
    contact_id: int,
    request: RecruiterStatusUpdate,
    job_service: JobService = Depends(get_job_service),
):
    db = job_service.session
    contact = await db.get(RecruiterContact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.status = request.status
    if request.notes is not None:
        contact.notes = request.notes
    if "Sent" in request.status:
        contact.last_contacted_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}")
async def delete_contact(
    contact_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    contact = await db.get(RecruiterContact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(contact)
    await db.commit()
    return {"success": True}


@router.get("/export")
async def export_crm(
    format: str = "csv", job_service: JobService = Depends(get_job_service)
):
    """Exports the Recruiter CRM data."""
    db = job_service.session
    stmt = select(RecruiterContact)
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    import pandas as pd
    import io
    from fastapi.responses import StreamingResponse

    df = pd.DataFrame([
        {
            "Name": c.name,
            "Title": c.title,
            "Company": c.company,
            "Status": c.status,
            "Email": c.email,
            "LinkedIn": c.linkedin_url,
            "Notes": c.notes,
        } for c in contacts
    ])

    output = io.BytesIO()
    if format == "csv":
        df.to_csv(output, index=False)
        media_type = "text/csv"
        filename = "recruiters_export.csv"
    else:
        df.to_excel(output, index=False)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "recruiters_export.xlsx"

    output.seek(0)
    return StreamingResponse(
        output,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# --- Outreach Generation ---


@router.post("/generate-outreach")
async def generate_outreach(
    request: OutreachGenerateRequest,
    job_service: JobService = Depends(get_job_service),
    engine: TaskEngine = Depends(get_task_engine),
):
    db = job_service.session
    contact = await db.get(RecruiterContact, request.recruiter_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Recruiter contact not found")

    resume = await db.get(Resume, request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Call AI TaskEngine with rich context
    result = await engine.generate_recruiter_outreach(
        recruiter_name=contact.name,
        recruiter_title=contact.title,
        company_name=contact.company,
        resume_content=resume.content,
        message_type=request.message_type,
        writing_style="Professional" # Default style, could be added to OutreachGenerateRequest
    )

    return {"success": True, "outreach": result["data"]}
