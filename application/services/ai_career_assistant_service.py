import logging
import time
from typing import Any, Dict, List, Optional

from application.dto.output.career_assistant_output import (
    GenerationMetadataDTO, GenerationResultDTO)
from application.ports.providers.interfaces import IAIProvider
from application.results.result import Failure, FailureType, Result
from application.services.career_context_builder import CareerContextBuilder
from application.services.fallback_generator import FallbackContentGenerator
from application.services.prompt_registry_service import PromptRegistryService
from application.services.prompt_template_service import PromptTemplateService
from domain.services.career_assistant.post_processing_service import \
    ContentPostProcessingService
from domain.services.career_assistant.safety_service import \
    ContentSafetyService
from domain.services.career_assistant.validation_service import \
    ContentValidationService
from domain.shared.value_objects import AIRequestPolicy

logger = logging.getLogger(__name__)


class AICareerAssistantService:
    """
    Unified orchestration layer for all AI content generation.
    Handles Prompting, Policy Enforcement, Execution, Safety, and Post-Processing.
    """

    def __init__(
        self,
        ai_provider: IAIProvider,
        prompt_service: PromptTemplateService,
        prompt_registry: PromptRegistryService,
        context_builder: CareerContextBuilder,
        validation_service: ContentValidationService,
        post_processor: ContentPostProcessingService,
        safety_service: ContentSafetyService,
    ):
        self._ai_provider = ai_provider
        self._prompt_service = prompt_service
        self._prompt_registry = prompt_registry
        self._context_builder = context_builder
        self._validation_service = validation_service
        self._post_processor = post_processor
        self._safety_service = safety_service

    async def generate_content(
        self,
        candidate_id: str,
        prompt_id: str,
        job_id: Optional[str] = None,
        custom_context: Optional[Dict[str, Any]] = None,
        content_type: str = "general",
        policy: Optional[AIRequestPolicy] = None,
    ) -> Result[GenerationResultDTO]:

        start_time = time.perf_counter()
        policy = policy or AIRequestPolicy()

        # 1. Assemble Context
        context = await self._context_builder.build_full_context(candidate_id, job_id)
        if custom_context:
            context.update(custom_context)

        # 2. Registry Check
        missing_vars = self._prompt_registry.validate_context(prompt_id, context)
        if missing_vars:
            return Result.validation_fail(
                f"Missing required context variables for {prompt_id}: {', '.join(missing_vars)}"
            )

        prompt_meta = self._prompt_registry.get_metadata(prompt_id)

        # 3. Render Prompt
        try:
            rendered_prompt = await self._prompt_service.render(
                prompt_id, context, version=prompt_meta.version if prompt_meta else None
            )
        except Exception as e:
            return Result.infra_fail(f"Prompt rendering failed: {e}")

        # 4. Call AI Provider with Policy
        try:
            ai_res = await self._ai_provider.generate(
                messages=[{"role": "user", "content": rendered_prompt}],
                config={
                    "max_tokens": policy.max_tokens,
                    "temperature": context.get("temperature", 0.1),
                },
            )
            raw_content = ai_res.get("data", "")
            meta = ai_res.get("meta", {})

        except Exception as e:
            logger.warning(f"AI Provider failed, triggering fallback: {e}")
            return self._handle_fallback(content_type, context, start_time)

        # 5. Output Safety Layer
        if self._safety_service.detect_prompt_leakage(raw_content):
            logger.error(f"Prompt leakage detected in {prompt_id} output.")
            return Result.business_fail(
                "Safety violation: Generated content contains prompt leakage."
            )

        pii_leaks = self._safety_service.detect_pii(raw_content)
        if pii_leaks:
            logger.warning(f"Potential PII detected in {prompt_id} output: {pii_leaks}")

        # 6. Post-Processing
        clean_content = self._post_processor.cleanup_formatting(raw_content)

        # 7. Quality Validation
        placeholders = self._validation_service.detect_placeholders(clean_content)
        missing_keywords = []
        if "job" in context:
            missing_keywords = self._validation_service.check_mandatory_keywords(
                clean_content, context["job"].get("required_skills", [])[:2]
            )

        quality_score = self._validation_service.calculate_quality_score(
            clean_content, placeholders, missing_keywords
        )

        # 8. Build Result
        duration = (time.perf_counter() - start_time) * 1000
        output = GenerationResultDTO(
            content=clean_content,
            quality_score=quality_score,
            metadata=GenerationMetadataDTO(
                provider=meta.get("provider", "unknown"),
                model=meta.get("model", "unknown"),
                tokens_used=meta.get("total_tokens", 0),
                latency_ms=duration,
                prompt_version=prompt_meta.version if prompt_meta else "unknown",
            ),
            suggested_edits=placeholders
            + [f"Missing keyword: {k}" for k in missing_keywords],
        )

        return Result.ok(output)

    def _handle_fallback(
        self, content_type: str, context: Dict[str, Any], start_time: float
    ) -> Result[GenerationResultDTO]:
        fallback_content = FallbackContentGenerator.generate(content_type, context)
        duration = (time.perf_counter() - start_time) * 1000

        output = GenerationResultDTO(
            content=fallback_content,
            quality_score=0.5,  # Fallback baseline
            metadata=GenerationMetadataDTO(
                provider="deterministic_fallback",
                model="jinja2_template",
                tokens_used=0,
                latency_ms=duration,
                is_fallback=True,
            ),
        )
        return Result.ok(output)
