from application.dto.input.career_assistant_input import BaseGenerationInputDTO
from application.dto.output.career_assistant_output import GenerationResultDTO
from application.results.result import Result
from application.services.ai_career_assistant_service import \
    AICareerAssistantService
from application.use_cases.base import ApplicationUseCase


class GenerateFollowUpEmailUseCase(
    ApplicationUseCase[BaseGenerationInputDTO, GenerationResultDTO]
):
    def __init__(self, ai_orchestrator: AICareerAssistantService):
        self._ai = ai_orchestrator

    async def _run(
        self, input_dto: BaseGenerationInputDTO
    ) -> Result[GenerationResultDTO]:
        return await self._ai.generate_content(
            candidate_id=input_dto.candidate_id,
            job_id=input_dto.job_id,
            prompt_id="application_follow_up",
            content_type="email",
        )
