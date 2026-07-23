from abc import ABC, abstractmethod
from typing import List, Optional
from core.schemas.job_listing import JobListingCreate

class BaseScraper(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique operational identifier string for the target job board."""
        pass

    @abstractmethod
    async def scrape(
        self, 
        search_query: str, 
        location: Optional[str] = None, 
        limit: int = 10, 
        job_type: str = "Full-Time"
    ) -> List[JobListingCreate]:
        """
        Harvests listings from the target board using standardized parameters.
        """
        pass
