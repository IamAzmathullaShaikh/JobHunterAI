from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.database.models import JobListing, AIAnalysis
from core.schemas.job_listing import JobListingCreate, JobListingRead

class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, dto: JobListingCreate) -> JobListingRead:
        """Persists a new job listing DTO into the database layer."""
        db_item = JobListing(**dto.model_dump())
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return JobListingRead.model_validate(db_item)

    async def bulk_create_ignore_duplicates(self, dtos: List[JobListingCreate]) -> List[JobListingRead]:
        """Saves new job listings while skipping items that already exist by job_id_raw."""
        saved_items: List[JobListingRead] = []
        for dto in dtos:
            existing = await self.get_by_raw_id(dto.job_id_raw)
            if not existing:
                saved = await self.create(dto)
                saved_items.append(saved)
        return saved_items

    async def get_by_raw_id(self, job_id_raw: str) -> Optional[JobListingRead]:
        """Retrieves a single listing by its raw external source ID."""
        stmt = select(JobListing).where(JobListing.job_id_raw == job_id_raw)
        result = await self.session.execute(stmt)
        db_item = result.scalar_one_or_none()
        return JobListingRead.model_validate(db_item) if db_item else None

    async def get_pending_analysis_jobs(self, limit: int = 20) -> List[JobListingRead]:
        """Fetches listings that do not have an associated AI analysis record yet."""
        stmt = (
            select(JobListing)
            .outerjoin(AIAnalysis)
            .where(AIAnalysis.id.is_(None))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        db_items = result.scalars().all()
        return [JobListingRead.model_validate(item) for item in db_items]