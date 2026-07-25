from typing import Any, Dict, Optional

from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from domain.shared.value_objects import CandidateId, JobId


class CareerContextBuilder:
    """
    Assembles complex business context into a flat structure for AI consumption.
    """

    def __init__(self, candidate_repo: ICandidateRepository, job_repo: IJobRepository):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo

    async def build_full_context(
        self, candidate_id: str, job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        context = {}

        # 1. Candidate Info
        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(candidate_id)
        )
        if candidate:
            context["candidate"] = {
                "name": candidate.full_name,
                "email": candidate.contact_info.email.value,
                "experience_years": candidate.total_years_experience,
                "skills": [s.name for s in candidate.skills],
                "summary": (
                    candidate.latest_resume().current_version.raw_text
                    if candidate.latest_resume()
                    else ""
                ),
            }

        # 2. Job Info
        if job_id:
            job = await self._job_repo.get_by_id(JobId.from_str(job_id))
            if job:
                context["job"] = {
                    "title": job.title,
                    "company": job.company_id,
                    "description": job.description,
                    "location": f"{job.location.city}, {job.location.country}",
                    "required_skills": job.required_skills,
                }

        # 3. Add timestamp and metadata
        from datetime import datetime

        context["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "platform": "JobHunterAI Pro",
        }

        return context
