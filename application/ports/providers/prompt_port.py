from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IPromptProvider(ABC):
    """
    Interface for loading versioned prompt templates.
    Templates can be stored in the file system, DB, or a dedicated CMS.
    """

    @abstractmethod
    async def get_template(self, prompt_id: str, version: Optional[str] = None) -> str:
        """
        Retrieves the raw prompt template for the given ID.
        """
        pass

    @abstractmethod
    def list_templates(self) -> Dict[str, str]:
        """
        Lists available templates and their current production versions.
        """
        pass
