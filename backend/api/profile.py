from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from database.connection import get_db_session
from database.models import UserProfile
from ai.resume_parser import ResumeParser
from schemas.user_profile import ParsedProfileDTO

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("/")
async def get_profile(db: AsyncSession = Depends(get_db_session)):
    stmt = select(UserProfile).order_by(UserProfile.updated_at.desc()).limit(1)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        return {"profile": None}
    return {"profile": profile}

@router.post("/parse")
async def parse_resume(payload: dict, db: AsyncSession = Depends(get_db_session)):
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Resume text is required.")

    parser = ResumeParser()
    try:
        parsed_dto = await parser.parse_resume(text)

        # Save to database
        db_profile = UserProfile(
            full_name=parsed_dto.full_name,
            total_experience_years=parsed_dto.total_experience_years,
            education=parsed_dto.education,
            key_skills=parsed_dto.key_skills,
            recommended_search_queries=parsed_dto.recommended_search_queries,
            experience_highlights=parsed_dto.experience_highlights,
            raw_resume_text=text
        )
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)

        return {"profile": db_profile}
    except Exception as e:
        # Fallback logic if AI fails
        fallback_profile = UserProfile(
            full_name="Local User",
            total_experience_years=0,
            key_skills=[],
            recommended_search_queries=["Software Engineer"],
            experience_highlights=["AI parsing failed, using fallback."]
        )
        db.add(fallback_profile)
        await db.commit()
        return {"profile": fallback_profile, "fallback": True, "error": str(e)}
