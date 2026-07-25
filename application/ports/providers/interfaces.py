from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.providers.ai.base import IAIProvider
from core.providers.scrapers.base import IScraperProvider
from domain.profile.entities import Certification, Education, Experience, Skill


class IFileParserProvider(ABC):
    """
    Interface for extracting raw text from various file formats (PDF, DOCX).
    """

    @abstractmethod
    async def extract_text(self, file_content: bytes, content_type: str) -> str:
        pass


class IResumeParserProvider(ABC):
    """
    Interface for converting raw resume text into structured domain components.
    """

    @abstractmethod
    async def parse(self, text: str) -> Dict[str, Any]:
        """
        Returns a dictionary containing candidate_info, skills, experience, etc.
        to be mapped into Domain entities.
        """
        pass
