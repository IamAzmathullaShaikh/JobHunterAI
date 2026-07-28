import logging
import re
from typing import List, Optional

logger = logging.getLogger("jobhunterai.deduplication")

class DeduplicationEngine:
    """
    Identifies and merges duplicate job listings using multiple signals.
    """

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r"[^a-zA-Z0-9]", "", text.lower())

    def are_duplicates(self, job1: dict, job2: dict, threshold: float = 0.85) -> bool:
        """
        Heuristic-based duplicate detection.
        Hardens company name matching to handle "Google" vs "Google LLC".
        """
        # 1. Exact ID Match
        if job1.get("job_id_raw") and job1.get("job_id_raw") == job2.get("job_id_raw"):
            return True

        # 2. Title + Company Normalized Match
        t1 = self._normalize(job1.get("title"))
        t2 = self._normalize(job2.get("title"))

        c1 = self._normalize(job1.get("company_name"))
        c2 = self._normalize(job2.get("company_name"))

        # Handle variations: "Google LLC" starts with "Google"
        company_match = c1 == c2 or (c1 and c2 and (c1.startswith(c2) or c2.startswith(c1)))

        if t1 == t2 and company_match:
            # Further check location if possible
            l1 = self._normalize(job1.get("location"))
            l2 = self._normalize(job2.get("location"))
            if not l1 or not l2 or l1 == l2:
                return True

        return False

    def deduplicate_batch(self, new_jobs: List[dict], existing_jobs: List[dict]) -> List[dict]:
        """
        Filters out duplicates from a new batch against existing records.
        """
        unique_jobs = []
        for new_job in new_jobs:
            is_dup = False
            for existing in existing_jobs:
                if self.are_duplicates(new_job, existing):
                    is_dup = True
                    break

            if not is_dup:
                # Also check against already processed in this batch
                for unique in unique_jobs:
                    if self.are_duplicates(new_job, unique):
                        is_dup = True
                        break

            if not is_dup:
                unique_jobs.append(new_job)

        return unique_jobs

deduplication_engine = DeduplicationEngine()
