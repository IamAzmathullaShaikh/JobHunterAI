from abc import ABC, abstractmethod
from typing import Any, Dict, List, Set


class IJobParserProvider(ABC):
    """
    Interface for extracting structured requirements from a raw job description.
    """

    @abstractmethod
    async def parse_job(self, raw_text: str) -> Dict[str, Any]:
        """
        Returns structured data like title, required_skills, preferred_skills,
        experience_level, etc.
        """
        pass


class IKeywordExtractorProvider(ABC):
    """
    Interface for extracting industry-specific keywords from text.
    """

    @abstractmethod
    async def extract_keywords(self, text: str) -> Set[str]:
        pass


class IEmbeddingProvider(ABC):
    """
    Interface for generating semantic embeddings for text.
    """

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        pass
