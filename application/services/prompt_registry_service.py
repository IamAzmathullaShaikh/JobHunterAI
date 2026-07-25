import logging
from typing import Dict, List, Optional

from application.ports.providers.prompt_port import IPromptProvider
from domain.shared.value_objects import PromptMetadata

logger = logging.getLogger(__name__)


class PromptRegistryService:
    """
    Manages prompt metadata, versions, and validation of expected variables.
    """

    def __init__(self, provider: IPromptProvider):
        self._provider = provider
        self._registry: Dict[str, PromptMetadata] = {
            "resume_tailoring": PromptMetadata(
                prompt_id="resume_tailoring",
                version="1.0.0",
                category="resume",
                expected_variables=["target_role", "candidate", "job"],
                output_type="text",
            ),
            "cover_letter_gen": PromptMetadata(
                prompt_id="cover_letter_gen",
                version="1.1.0",
                category="outreach",
                expected_variables=["candidate", "job", "tone"],
                output_type="text",
            ),
            "recruiter_outreach": PromptMetadata(
                prompt_id="recruiter_outreach",
                version="1.0.0",
                category="outreach",
                expected_variables=[
                    "platform",
                    "recipient",
                    "company",
                    "job",
                    "candidate",
                ],
                output_type="text",
            ),
            "executive_summary": PromptMetadata(
                prompt_id="executive_summary",
                version="1.0.0",
                category="report",
                expected_variables=["kpis", "funnel", "top_recommendation"],
                output_type="text",
            ),
        }

    def get_metadata(self, prompt_id: str) -> Optional[PromptMetadata]:
        return self._registry.get(prompt_id)

    def validate_context(self, prompt_id: str, context: Dict[str, any]) -> List[str]:
        """Checks if all required variables for a prompt are present in the context."""
        meta = self.get_metadata(prompt_id)
        if not meta:
            return [f"Prompt ID {prompt_id} not found in registry."]

        missing = []
        for var in meta.expected_variables:
            if var not in context:
                missing.append(var)
        return missing

    def list_all(self) -> List[PromptMetadata]:
        return list(self._registry.values())
