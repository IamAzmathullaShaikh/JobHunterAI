import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.ports.providers.prompt_port import IPromptProvider
from application.services.prompt_template_service import PromptTemplateService


@pytest.mark.asyncio
async def test_prompt_template_consistency():
    """
    Ensures that prompt templates render with expected variables
    to prevent regressions in LLM instruction sets.
    """
    mock_provider = MagicMock(spec=IPromptProvider)
    # Define a snapshot of a production template
    snapshot = "Write a letter for {{ name }}"
    mock_provider.get_template = AsyncMock(return_value=snapshot)

    service = PromptTemplateService(mock_provider)

    # Render with context
    rendered = await service.render("test_id", {"name": "Alex"})

    assert rendered == "Write a letter for Alex"
    assert "Alex" in rendered
    print("✅ Prompt snapshot consistency verified.")


if __name__ == "__main__":
    asyncio.run(test_prompt_template_consistency())
