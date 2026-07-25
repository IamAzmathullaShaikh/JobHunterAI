from application.dto.input.career_assistant_input import CareerAdviceInputDTO
from application.dto.output.career_assistant_output import GenerationResultDTO
from application.results.result import Result
from application.services.ai_career_assistant_service import \
    AICareerAssistantService
from application.use_cases.base import ApplicationUseCase


class GenerateCareerAdviceUseCase(
    ApplicationUseCase[CareerAdviceInputDTO, GenerationResultDTO]
):
    def __init__(self, ai_orchestrator: AICareerAssistantService):
        self._ai = ai_orchestrator

    async def _run(
        self, input_dto: CareerAdviceInputDTO
    ) -> Result[GenerationResultDTO]:
        return await self._ai.generate_content(
            candidate_id=input_dto.candidate_id,
            prompt_id="career_guidance",
            custom_context={
                "topic": input_dto.topic,
                "status": input_dto.current_status,
            },
        )
