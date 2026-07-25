import logging
import os
from typing import Any, Dict, Optional

from application.ports.providers.prompt_port import IPromptProvider

logger = logging.getLogger(__name__)


class FileSystemPromptProvider(IPromptProvider):
    """
    Loads templates from the /prompts directory.
    """

    def __init__(self, base_path: str = "backend/prompts"):
        self._base_path = base_path

    async def get_template(self, prompt_id: str, version: Optional[str] = None) -> str:
        # Simple file lookup. Versioning could be prompt_id_v1.j2
        filename = f"{prompt_id}.j2"
        path = os.path.join(self._base_path, filename)

        if not os.path.exists(path):
            logger.error(f"Template not found: {path}")
            raise FileNotFoundError(f"Prompt template {prompt_id} not found.")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def list_templates(self) -> Dict[str, str]:
        templates = {}
        if not os.path.exists(self._base_path):
            return {}
        for f in os.listdir(self._base_path):
            if f.endswith(".j2"):
                templates[f.replace(".j2", "")] = "1.0"
        return templates
