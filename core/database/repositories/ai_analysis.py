import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger

from database.models import AIAnalysis
from schemas.ai import AIAnalysisCreate, AIAnalysisDTO

class AIAnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_analysis(self, job_id: int, analysis_data: AIAnalysisCreate) -> AIAnalysisDTO:
        """Saves structured OpenAI output models mapped directly to an explicit target job ID."""
        logger.info(f"Saving match evaluation vectors for internal job mapping index: {job_id}")
        
        db_analysis = AIAnalysis(
            job_id=job_id,
            match_score=analysis_data.match_score,
            fit_summary=analysis_data.fit_summary,
            keywords_matched=json.dumps(analysis_data.keywords_matched),
            keywords_missing=json.dumps(analysis_data.keywords_missing)
        )
        
        self.session.add(db_analysis)
        await self.session.flush()
        
        # Build out return item converting local strings to validation schemas
        return AIAnalysisDTO(
            id=db_analysis.id,
            job_id=db_analysis.job_id,
            match_score=db_analysis.match_score,
            fit_summary=db_analysis.fit_summary,
            keywords_matched=analysis_data.keywords_matched,
            keywords_missing=analysis_data.keywords_missing,
            suggested_resume_path=db_analysis.suggested_resume_path,
            suggested_cover_letter_path=db_analysis.suggested_cover_letter_path,
            analyzed_at=db_analysis.analyzed_at
        )

    async def get_by_job_id(self, job_id: int) -> Optional[AIAnalysisDTO]:
        """Retrieves structured scoring criteria reports for a specific job entry."""
        stmt = select(AIAnalysis).where(AIAnalysis.job_id == job_id)
        result = await self.session.execute(stmt)
        db_analysis = result.scalar_one_or_none()
        
        if not db_analysis:
            return None
            
        return AIAnalysisDTO(
            id=db_analysis.id,
            job_id=db_analysis.job_id,
            match_score=db_analysis.match_score,
            fit_summary=db_analysis.fit_summary,
            keywords_matched=json.loads(db_analysis.keywords_matched),
            keywords_missing=json.loads(db_analysis.keywords_missing),
            suggested_resume_path=db_analysis.suggested_resume_path,
            suggested_cover_letter_path=db_analysis.suggested_cover_letter_path,
            analyzed_at=db_analysis.analyzed_at
        )