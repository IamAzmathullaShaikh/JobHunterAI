import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.dto.input.career_assistant_input import CoverLetterInputDTO
from application.ports.providers.interfaces import IAIProvider
from application.ports.providers.prompt_port import IPromptProvider
from application.results.result import Result
from application.services.ai_career_assistant_service import \
    AICareerAssistantService
from application.services.career_context_builder import CareerContextBuilder
from application.services.prompt_registry_service import PromptRegistryService
from application.services.prompt_template_service import PromptTemplateService
from domain.services.career_assistant.post_processing_service import \
    ContentPostProcessingService
from domain.services.career_assistant.safety_service import \
    ContentSafetyService
from domain.services.career_assistant.validation_service import \
    ContentValidationService


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_ai_career_assistant_success():
    # 1. Mocks
    mock_ai = MagicMock(spec=IAIProvider)
    mock_ai.generate = AsyncMock(
        return_value={
            "data": "This is a tailored cover letter with [Placeholder].",
            "meta": {"provider": "groq", "total_tokens": 100},
        }
    )

    mock_prompt_prov = MagicMock(spec=IPromptProvider)
    mock_prompt_prov.get_template = AsyncMock(
        return_value="Write a cover letter for {{ candidate.name }}"
    )

    mock_builder = MagicMock(spec=CareerContextBuilder)
    mock_builder.build_full_context = AsyncMock(
        return_value={"candidate": {"name": "Alex"}}
    )

    mock_registry = MagicMock(spec=PromptRegistryService)
    mock_registry.validate_context.return_value = []
    mock_registry.get_metadata.return_value = MagicMock(version="1.0.0")

    mock_safety = MagicMock(spec=ContentSafetyService)
    mock_safety.detect_prompt_leakage.return_value = False
    mock_safety.detect_pii.return_value = []

    orchestrator = AICareerAssistantService(
        ai_provider=mock_ai,
        prompt_service=PromptTemplateService(mock_prompt_prov),
        prompt_registry=mock_registry,
        context_builder=mock_builder,
        validation_service=ContentValidationService(),
        post_processor=ContentPostProcessingService(),
        safety_service=mock_safety,
    )

    # 2. Run
    res = await orchestrator.generate_content(
        candidate_id="c1", prompt_id="test_p", content_type="cover_letter"
    )

    # 3. Assert
    assert res.is_success
    assert "tailored cover letter" in res.unwrap().content
    assert res.unwrap().quality_score < 1.0  # Penalized for [Placeholder]
    assert "[Placeholder]" in res.unwrap().suggested_edits[0]


@async_test
async def test_ai_career_assistant_fallback():
    # 1. AI Provider fails
    mock_ai = MagicMock(spec=IAIProvider)
    mock_ai.generate = AsyncMock(side_effect=RuntimeError("API Down"))

    mock_prompt_prov = MagicMock(spec=IPromptProvider)
    mock_prompt_prov.get_template = AsyncMock(return_value="...")

    mock_builder = MagicMock(spec=CareerContextBuilder)
    mock_builder.build_full_context = AsyncMock(
        return_value={"job": {"title": "Engineer"}}
    )

    mock_registry = MagicMock(spec=PromptRegistryService)
    mock_registry.validate_context.return_value = []
    mock_registry.get_metadata.return_value = MagicMock(version="1.0.0")

    mock_safety = MagicMock(spec=ContentSafetyService)
    mock_safety.detect_prompt_leakage.return_value = False
    mock_safety.detect_pii.return_value = []

    orchestrator = AICareerAssistantService(
        ai_provider=mock_ai,
        prompt_service=PromptTemplateService(mock_prompt_prov),
        prompt_registry=mock_registry,
        context_builder=mock_builder,
        validation_service=ContentValidationService(),
        post_processor=ContentPostProcessingService(),
        safety_service=mock_safety,
    )

    # 2. Run
    res = await orchestrator.generate_content(
        candidate_id="c1", prompt_id="test_p", content_type="cover_letter"
    )

    # 3. Assert - Should return deterministic fallback
    assert res.is_success
    assert res.unwrap().metadata.is_fallback == True
    assert "Dear Hiring Manager" in res.unwrap().content
