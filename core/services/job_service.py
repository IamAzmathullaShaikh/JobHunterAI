import logging
import re
from typing import List, Set, Tuple

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.ai.matcher import JobMatcher
from core.database.models import (AIAnalysis, ApplicationStatus,
                                  JobApplication, JobListing)
from core.deduplication_engine import deduplication_engine
from core.enrichment_engine import enrichment_engine
from core.schemas.job_listing import JobListingCreate
from core.scrapers.manager import ScraperManager
from core.ai.smart_router import route as smart_route

from core.utils.logging_config import record_audit_log

logger = logging.getLogger("jobhunterai.job_service")


class JobService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.scraper_manager = ScraperManager(session=session)
        self.matcher = JobMatcher()

    async def search_live(self, query: str, location: str = "Remote", limit: int = 20) -> List[Dict[str, Any]]:
        """Live multi-platform scraping using JobSpy fleet."""
        try:
            from jobspy import scrape_jobs
            if not scrape_jobs:
                logger.error("JobSpy not installed.")
                return []

            # Note: JobSpy is sync, for production we might wrap this in run_in_executor
            logger.info(f"Searching for '{query}' in '{location}'...")
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "glassdoor", "google"],
                search_term=query,
                location=location,
                results_wanted=limit,
                hours_old=72
            )
            return jobs.to_dict("records") if not jobs.empty else []
        except Exception as e:
            logger.error(f"Live search failed: {e}")
            return []

    def _normalize_str(self, text: str) -> str:
        """Normalizes title/company strings for reliable duplicate detection."""
        if not text:
            return ""
        return re.sub(r"[^a-zA-Z0-9]", "", text.lower())

    async def get_applied_and_existing_keys(
        self,
    ) -> Tuple[Set[str], Set[Tuple[str, str]]]:
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
            ApplicationStatus.OFFERED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ARCHIVED,
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
        job_type: str = "Full-Time",
    ) -> List[JobListing]:
        """Scrapes jobs across all fleet engines, with transparent local fallback."""
        logger.info(f"Initiating Fleet Search for '{search_query}' in '{location}'...")

        # 1. Primary Fleet Discovery (Parallel Multi-source)
        raw_listings: List[JobListingCreate] = await self.scraper_manager.run_all(
            search_query=search_query,
            location=location,
            limit_per_site=limit,
            job_type=job_type,
        )

        # 2. Transparent Fallback (JobSpy)
        if not raw_listings:
            logger.warning("Fleet search returned 0 results. Triggering local JobSpy fallback...")
            try:
                from core.scraper import local_scrape
                local_res = await local_scrape({"query": search_query, "location": location, "limit": limit})
                # Convert dict to JobListingCreate objects
                for item in local_res.get("data", []):
                    raw_listings.append(JobListingCreate(
                        job_id_raw=str(item.get("job_id", random.randint(1000, 9999))),
                        title=item.get("title", "Role"),
                        company_name=item.get("company_name", "Company"),
                        location=item.get("location", location),
                        source="jobspy_fallback",
                        url=item.get("url", "#"),
                        description_raw=item.get("description_raw", "")
                    ))
            except Exception as e:
                logger.error(f"Fallback failed: {e}")

        # 3. Deduplication against DB and Batch
        existing_stmt = select(JobListing)
        existing_res = await self.session.execute(existing_stmt)
        all_existing = [j.__dict__ for j in existing_res.scalars().all()]

        unique_raw = deduplication_engine.deduplicate_batch(
            [item.model_dump() for item in raw_listings],
            all_existing
        )

        # 2. Parallel Enrichment with Semaphore and Error Boundaries
        logger.info(f"Enriching {len(unique_raw)} unique listings...")
        semaphore = asyncio.Semaphore(2) # Strict limit to prevent API rate limits

        async def enrich_and_map(item_dict: dict):
            async with semaphore:
                try:
                    enriched_data = await enrichment_engine.enrich_job(item_dict.get("description_raw", ""))
                    return JobListing(
                        job_id_raw=item_dict.get("job_id_raw"),
                        title=item_dict.get("title"),
                        company_name=item_dict.get("company_name"),
                        location=item_dict.get("location"),
                        work_place_type=enriched_data.get("work_model") or item_dict.get("work_place_type"),
                        job_type=item_dict.get("job_type"),
                        source=item_dict.get("source"),
                        url=item_dict.get("url"),
                        description_raw=item_dict.get("description_raw"),
                        description_clean=item_dict.get("description_clean"),
                        # New fields
                        required_skills=enriched_data.get("required_skills"),
                        seniority=enriched_data.get("seniority"),
                        technologies=enriched_data.get("technologies"),
                        benefits=enriched_data.get("benefits"),
                    )
                except Exception as e:
                    logger.warning(f"Enrichment failed for '{item_dict.get('title')}': {e}. Saving with raw data.")
                    return JobListing(
                        job_id_raw=item_dict.get("job_id_raw"),
                        title=item_dict.get("title"),
                        company_name=item_dict.get("company_name"),
                        location=item_dict.get("location"),
                        work_place_type=item_dict.get("work_place_type"),
                        job_type=item_dict.get("job_type"),
                        source=item_dict.get("source"),
                        url=item_dict.get("url"),
                        description_raw=item_dict.get("description_raw"),
                        description_clean=item_dict.get("description_clean"),
                    )

        enrichment_tasks = [enrich_and_map(item) for item in unique_raw]
        unique_new_models = await asyncio.gather(*enrichment_tasks)

        if unique_new_models:
            self.session.add_all(unique_new_models)
            await self.session.commit()
            logger.info(
                f"Persisted {len(unique_new_models)} deduplicated new job listings to database."
            )

            # --- Milestone 5: Audit Logging ---
            await record_audit_log(
                self.session,
                action="SCRAPE",
                resource_type="JOB_LISTING",
                payload={"count": len(unique_new_models), "query": search_query}
            )
        else:
            logger.info(
                "No new unique listings found (all scraped roles were duplicates or previously applied)."
            )

        return unique_new_models

    async def purge_duplicates_and_applied(self) -> Tuple[int, int]:
        """
        Maintenance routine:
        1. Deletes duplicate job listings from the database (keeps newest ID).
        2. Removes job listings that have an APPLIED status if they are cluttering the active pool.
        Returns (duplicates_purged_count, applied_purged_count).
        """
        logger.info(
            "Executing database purge for duplicate and applied job listings..."
        )

        # 1. Fetch all listings ordered by date_scraped descending
        stmt = (
            select(JobListing)
            .options(selectinload(JobListing.application))
            .order_by(JobListing.date_scraped.desc())
        )

        res = await self.session.execute(stmt)
        listings = res.scalars().all()

        seen_ids: Set[str] = set()
        seen_tuples: Set[Tuple[str, str]] = set()

        ids_to_delete: List[int] = []
        applied_deleted_count = 0

        excluded_statuses = {
            ApplicationStatus.APPLIED,
            ApplicationStatus.INTERVIEWING,
            ApplicationStatus.OFFERED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ARCHIVED,
        }

        for job in listings:
            raw_id = job.job_id_raw
            clean_title = self._normalize_str(job.title)
            clean_company = self._normalize_str(job.company_name)
            tuple_key = (clean_title, clean_company)

            # Check if job was applied to
            is_applied = job.application and job.application.status in excluded_statuses

            # Duplicate check
            is_duplicate = (raw_id and raw_id in seen_ids) or (
                clean_title and clean_company and tuple_key in seen_tuples
            )

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
            logger.info(
                f"Purged {len(ids_to_delete)} duplicate listing records from core.database."
            )

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
                    user_profile=user_profile,
                )

                ai_record = AIAnalysis(
                    job_id=job.id,
                    match_score=analysis.match_score,
                    fit_summary=analysis.fit_summary,
                    keywords_matched=analysis.keywords_matched,
                    keywords_missing=analysis.keywords_missing,
                )
                self.session.add(ai_record)
                analyzed_count += 1
            except Exception as e:
                logger.error(f"Error evaluating AI match for Job ID {job.id}: {str(e)}")

        if analyzed_count > 0:
            await self.session.commit()

        return analyzed_count
