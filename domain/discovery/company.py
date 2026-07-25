from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from domain.discovery.entities import Job
from domain.shared.value_objects import CompanyId


@dataclass
class Company:
    id: CompanyId
    name: str
    website_url: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    _jobs: List[Job] = field(default_factory=list)

    @property
    def jobs(self) -> Tuple[Job, ...]:
        return tuple(self._jobs)

    def publish_job(self, job: Job):
        if str(job.company_id) != str(self.id):
            job.company_id = str(self.id)
        self._jobs.append(job)

    def remove_job(self, job_id: str):
        self._jobs = [j for s in self._jobs if str(j.id) != job_id]

    def active_jobs(self) -> List[Job]:
        return [j for j in self._jobs if j.is_open()]
