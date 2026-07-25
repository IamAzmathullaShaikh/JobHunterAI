from abc import ABC, abstractmethod
from typing import Any, Dict


class ICompanyKnowledgeProvider(ABC):
    """
    Interface for AI-enriched company research and culture insights.
    """

    @abstractmethod
    async def get_company_profile(self, company_name: str) -> Dict[str, Any]:
        """
        Returns overview, tech stack, and typical interview themes for the company.
        """
        pass
