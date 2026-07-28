import logging
from typing import Any, Dict, List
import pdfplumber
from sqlalchemy.ext.asyncio import AsyncSession
from core.ai.matcher import JobMatcher
from core.resume_engine import resume_engine
from core.caching import AICache

from core.ai.resume_parser import ResumeParser
from core.database.models import UserProfile, MatchHistory
from sqlalchemy import select
from core.schemas.user_profile import ParsedProfileDTO
from core.utils.document_processor import extract_text_from_bytes
from core.utils.logging_config import record_audit_log

logger = logging.getLogger("jobhunterai.resume_service")

class ResumeService:
    """Specialized service for Resume intelligence and document processing."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.cache = AICache(db_session)
        self.matcher = JobMatcher()
        self.parser = ResumeParser()

    async def parse_text(self, text: str) -> UserProfile:
        """Parses resume text into a UserProfile model."""
        parsed_dto = await self.parser.parse_resume(text)

        profile = UserProfile(
            full_name=parsed_dto.full_name,
            total_experience_years=parsed_dto.total_experience_years,
            education=parsed_dto.education,
            key_skills=parsed_dto.key_skills,
            recommended_search_queries=parsed_dto.recommended_search_queries,
            experience_highlights=parsed_dto.experience_highlights,
            raw_resume_text=text,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        # --- Milestone 5: Audit Logging ---
        await record_audit_log(
            self.db,
            action="CREATE",
            resource_type="PROFILE",
            resource_id=str(profile.id),
            payload={"name": profile.full_name}
        )

        return profile

    async def process_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Extracts text from a file and returns parsed result."""
        text = extract_text_from_bytes(file_bytes, filename)
        if not text:
            return {"success": False, "error": "Failed to extract text from file."}

        # Check cache
        cached = await self.cache.get(text[:5000])
        if cached:
            return {"success": True, "source": "cache", "data": cached}

        return {"success": True, "source": "extracted", "text": text}

    async def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Legacy PDF parsing for backend temp files."""
        with open(file_path, "rb") as f:
            return await self.process_file(f.read(), file_path)
        """Extracts text and identifies structure from a PDF resume."""
        logger.info(f"Processing PDF: {file_path}")
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

            # Check cache for identical content
            cached = await self.cache.get(text[:5000])
            if cached:
                return {"success": True, "source": "cache", "data": cached}

            return {
                "success": True,
                "source": "local_pypdf",
                "data": {"raw_text": text, "length": len(text)},
            }
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_fit(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Performs deep ATS compatibility analysis."""
        return await self.matcher.analyze_fit(job_description, resume_text)

    async def tailor_bullets(self, bullets: List[str], job_description: str) -> Dict[str, Any]:
        """Optimizes resume bullets for a specific role."""
        return await resume_engine.tailor_bullets(bullets, job_description)
