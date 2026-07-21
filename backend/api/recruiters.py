from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.connection import get_db_session
from core.enricher import enricher

router = APIRouter(prefix="/api/recruiters", tags=["recruiters"])

@router.post("/find")
async def find_recruiters(payload: dict, db: AsyncSession = Depends(get_db_session)):
    company = payload.get("company_name")
    dept = payload.get("department", "Engineering")

    if not company:
        raise HTTPException(status_code=400, detail="Company name is required.")

    leads = await enricher.find_decision_makers(company, dept)

    # Optional: Draft emails for each lead if resume context is provided
    resume_text = payload.get("resume_text")
    job_title = payload.get("job_title", "target position")
    user_name = payload.get("user_name", "Candidate")

    results = []
    for lead in leads:
        draft = None
        if resume_text:
            draft_res = await enricher.draft_outreach(
                resume_text, job_title, company, lead["person_name"], user_name
            )
            draft = draft_res.get("data") if draft_res.get("success") else None

        results.append({**lead, "draft_email": draft})

    return results
