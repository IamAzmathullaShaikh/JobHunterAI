import base64
import io
import pdfplumber
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from core.database.connection import get_db_session
from core.database.models import UserProfile
from core.ai.resume_parser import ResumeParser
from core.schemas.user_profile import ParsedProfileDTO
from core.utils.logger import logger

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("")
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
    file_base64 = payload.get("fileBase64")

    if not text and not file_base64:
        raise HTTPException(status_code=400, detail="Resume text or file is required.")

    # Handle PDF extraction if file is provided
    if file_base64:
        try:
            logger.info("Decoding and extracting text from PDF upload...")
            # Remove header if present (e.g. data:application/pdf;base64,...)
            if "," in file_base64:
                file_base64 = file_base64.split(",")[1]

            pdf_bytes = base64.b64decode(file_base64)
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""

            if not text.strip():
                raise ValueError("Could not extract any text from the provided PDF.")
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")

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
        logger.warning(f"AI parsing failed, using heuristic fallback. Error: {e}")
        # Use heuristic fallback already implemented in ResumeParser's router.route
        # But if even that failed, provide a manual dummy fallback here
        fallback_profile = UserProfile(
            full_name="Candidate",
            total_experience_years=0,
            key_skills=[],
            recommended_search_queries=["Software Engineer"],
            experience_highlights=["System fallback used due to processing error."]
        )
        db.add(fallback_profile)
        await db.commit()
        return {"profile": fallback_profile, "fallback": True, "error": str(e)}
