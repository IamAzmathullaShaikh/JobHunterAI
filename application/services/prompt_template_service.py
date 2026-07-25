import logging
from typing import Any, Dict, Optional

from jinja2 import Template

from application.ports.providers.prompt_port import IPromptProvider

logger = logging.getLogger(__name__)


class PromptTemplateService:
    """
    Handles prompt rendering using Jinja2 and manages template versioning.
    """

    def __init__(self, provider: IPromptProvider):
        self._provider = provider

    async def render(
        self, prompt_id: str, context: Dict[str, Any], version: Optional[str] = None
    ) -> str:
        """
        Loads a template and injects context variables.
        """
        try:
            template_str = await self._provider.get_template(prompt_id, version)
            template = Template(template_str)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render prompt {prompt_id}: {e}")
            raise RuntimeError(f"Prompt rendering failed: {str(e)}")

    def get_metadata(self, prompt_id: str) -> Dict[str, str]:
        return {
            "prompt_id": prompt_id,
            "engine": "jinja2",
            "provider": self._provider.__class__.__name__,
        }
