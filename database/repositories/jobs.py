import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger

from database.models import JobListing
from schemas.job import JobListingCreate, JobListingDTO

class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job_data: JobListingCreate) -> JobListingDTO:
        """Persists a new scraped job listing to the database."""
        logger.debug(f"Inserting job listing: {job_data.title} at {job_data.company_name}")
        
        db_job = JobListing(
            job_id_raw=job_data.job_id_raw,
            title=job_data.title,
            company_name=job_data.company_name,
            location=job_data.location,
            work_place_type=job_data.work_place_type,
            source=job_data.source,
            url=job_data.url,
            description_raw=job_data.description_raw,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            salary_currency=job_data.salary_currency,
            date_posted=job_data.date_posted
        )
        
        self.session.add(db_job)
        await self.session.flush()  # Populates the primary key ID
        return JobListingDTO.model_validate(db_job)

    async def get_by_raw_id(self, job_id_raw: str) -> Optional[JobListingDTO]:
        """Checks if a job has already been scraped using the unique site token."""
        stmt = select(JobListing).where(JobListing.job_id_raw == job_id_raw)
        result = await self.session.execute(stmt)
        db_job = result.scalar_one_or_none()
        
        if db_job:
            return JobListingDTO.model_validate(db_job)
        return None

    async def get_all_active(self, limit: int = 100, offset: int = 0) -> List[JobListingDTO]:
        """Fetches batch historical entries sorted by execution entry times."""
        stmt = select(JobListing).order_by(JobListing.date_scraped.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        db_jobs = result.scalars().all()
        
        return [JobListingDTO.model_validate(job) for job in db_jobs]

    async def update_clean_description(self, job_id: int, clean_text: str) -> None:
        """Applies parsed, normalized markdown text over noisy initial raw HTML strings."""
        stmt = select(JobListing).where(JobListing.id == job_id)
        result = await self.session.execute(stmt)
        db_job = result.scalar_one_or_none()
        if db_job:
            db_job.description_clean = clean_text