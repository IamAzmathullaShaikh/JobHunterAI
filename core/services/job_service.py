import re
from typing import List, Set, Tuple
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import JobListing, JobApplication, ApplicationStatus, AIAnalysis
from scrapers.manager import ScraperManager
from schemas.job_listing import JobListingCreate
from ai.matcher import JobMatcher
from utils.logger import logger

class JobService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.scraper_manager = ScraperManager(session=session)
        self.matcher = JobMatcher()

    def _normalize_str(self, text: str) -> str:
        """Normalizes title/company strings for reliable duplicate detection."""
        if not text:
            return ""
        return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

    async def get_applied_and_existing_keys(self) -> Tuple[Set[str], Set[Tuple[str, str]]]:
        """
        Returns sets of job_id_raw and (title_clean, company_clean) tuples for jobs 
        that either already exist in the DB or have been applied to/processed.
        """
        # Fetch all existing job IDs and normalized title+company pairs
        stmt = select(JobListing).options(selectinload(JobListing.application))
        res = await self.session.execute(stmt)
        listings = res.scalars().all()

        existing_ids: Set[str] = set()
        existing_title_company: Set[Tuple[str, str]] = set()

        # Excluded application statuses (applied, interviewing, offer, rejected, archived)
        excluded_statuses = {
            ApplicationStatus.APPLIED,
            ApplicationStatus.INTERVIEWING,
            ApplicationStatus.OFFER,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ARCHIVED
        }

        for job in listings:
            if job.job_id_raw:
                existing_ids.add(job.job_id_raw)
            
            clean_title = self._normalize_str(job.title)
            clean_company = self._normalize_str(job.company_name)
            
            if clean_title and clean_company:
                existing_title_company.add((clean_title, clean_company))

            # If job has an active application in an excluded state, ensure ID & tuple are tracked
            if job.application and job.application.status in excluded_statuses:
                if job.job_id_raw:
                    existing_ids.add(job.job_id_raw)
                existing_title_company.add((clean_title, clean_company))

        return existing_ids, existing_title_company

    async def discover_new_listings(
        self, 
        search_query: str, 
        location: str = "India", 
        limit: int = 10, 
        job_type: str = "Full-Time"
    ) -> List[JobListing]:
        """Scrapes jobs across all fleet engines, stripping out duplicates and applied jobs."""
        logger.info(f"Initiating job ingestion for '{search_query}' in '{location}'...")
        
        # Fetch existing/applied keys from DB
        existing_ids, existing_title_company = await self.get_applied_and_existing_keys()

        # Execute multi-site scraping fleet
        raw_listings: List[JobListingCreate] = await self.scraper_manager.run_all(
            search_query=search_query,
            location=location,
            limit_per_site=limit,
            job_type=job_type
        )

        seen_batch_ids: Set[str] = set()
        seen_batch_tuples: Set[Tuple[str, str]] = set()
        unique_new_models: List[JobListing] = []

        for item in raw_listings:
            raw_id = item.job_id_raw
            clean_title = self._normalize_str(item.title)
            clean_company = self._normalize_str(item.company_name)
            tuple_key = (clean_title, clean_company)

            # 1. Skip if already in database or marked as applied
            if raw_id in existing_ids or tuple_key in existing_title_company:
                logger.debug(f"Skipping existing/applied job: '{item.title}' at '{item.company_name}'")
                continue

            # 2. Skip duplicate entries within the current scrape batch
            if raw_id in seen_batch_ids or tuple_key in seen_batch_tuples:
                logger.debug(f"Skipping in-batch duplicate: '{item.title}' at '{item.company_name}'")
                continue

            # Track unique entry
            seen_batch_ids.add(raw_id)
            seen_batch_tuples.add(tuple_key)

            db_model = JobListing(
                job_id_raw=item.job_id_raw,
                title=item.title,
                company_name=item.company_name,
                location=item.location,
                work_place_type=item.work_place_type,
                job_type=item.job_type,
                source=item.source,
                url=item.url,
                description_raw=item.description_raw,
                description_clean=item.description_clean
            )
            unique_new_models.append(db_model)

        if unique_new_models:
            self.session.add_all(unique_new_models)
            await self.session.commit()
            logger.success(f"Persisted {len(unique_new_models)} deduplicated new job listings to database.")
        else:
            logger.info("No new unique listings found (all scraped roles were duplicates or previously applied).")

        return unique_new_models

    async def purge_duplicates_and_applied(self) -> Tuple[int, int]:
        """
        Maintenance routine:
        1. Deletes duplicate job listings from the database (keeps newest ID).
        2. Removes job listings that have an APPLIED status if they are cluttering the active pool.
        Returns (duplicates_purged_count, applied_purged_count).
        """
        logger.info("Executing database purge for duplicate and applied job listings...")
        
        # 1. Fetch all listings ordered by date_scraped descending
        stmt = select(JobListing).options(
            selectinload(JobListing.application)
        ).order_by(JobListing.date_scraped.desc())
        
        res = await self.session.execute(stmt)
        listings = res.scalars().all()

        seen_ids: Set[str] = set()
        seen_tuples: Set[Tuple[str, str]] = set()

        ids_to_delete: List[int] = []
        applied_deleted_count = 0

        excluded_statuses = {
            ApplicationStatus.APPLIED,
            ApplicationStatus.INTERVIEWING,
            ApplicationStatus.OFFER,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ARCHIVED
        }

        for job in listings:
            raw_id = job.job_id_raw
            clean_title = self._normalize_str(job.title)
            clean_company = self._normalize_str(job.company_name)
            tuple_key = (clean_title, clean_company)

            # Check if job was applied to
            is_applied = job.application and job.application.status in excluded_statuses

            # Duplicate check
            is_duplicate = (raw_id and raw_id in seen_ids) or (clean_title and clean_company and tuple_key in seen_tuples)

            if is_duplicate:
                ids_to_delete.append(job.id)
            elif is_applied:
                # Track as seen so future duplicates of this applied job are also dropped
                if raw_id:
                    seen_ids.add(raw_id)
                seen_tuples.add(tuple_key)
            else:
                if raw_id:
                    seen_ids.add(raw_id)
                seen_tuples.add(tuple_key)

        if ids_to_delete:
            del_stmt = delete(JobListing).where(JobListing.id.in_(ids_to_delete))
            await self.session.execute(del_stmt)
            await self.session.commit()
            logger.success(f"Purged {len(ids_to_delete)} duplicate listing records from database.")

        return len(ids_to_delete), applied_deleted_count

    async def process_pending_analyses(self, user_profile: str) -> int:
        """Evaluates unanalyzed jobs against the user's profile using Groq LLM."""
        stmt = select(JobListing).where(~JobListing.ai_analysis.has())
        result = await self.session.execute(stmt)
        pending_jobs = result.scalars().all()

        if not pending_jobs:
            return 0

        analyzed_count = 0
        for job in pending_jobs:
            try:
                analysis = await self.matcher.evaluate_match(
                    job_description=job.description_raw or job.title,
                    user_profile=user_profile
                )
                
                ai_record = AIAnalysis(
                    job_id=job.id,
                    match_score=analysis.match_score,
                    fit_summary=analysis.fit_summary,
                    keywords_matched=",".join(analysis.keywords_matched),
                    keywords_missing=",".join(analysis.keywords_missing)
                )
                self.session.add(ai_record)
                analyzed_count += 1
            except Exception as e:
                logger.error(f"Error evaluating AI match for Job ID {job.id}: {str(e)}")

        if analyzed_count > 0:
            await self.session.commit()

        return analyzed_count