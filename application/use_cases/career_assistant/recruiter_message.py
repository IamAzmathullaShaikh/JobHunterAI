from application.dto.input.career_assistant_input import \
    OutreachMessageInputDTO
from application.dto.output.career_assistant_output import GenerationResultDTO
from application.results.result import Result
from application.services.ai_career_assistant_service import \
    AICareerAssistantService
from application.use_cases.base import ApplicationUseCase


class GenerateRecruiterMessageUseCase(
    ApplicationUseCase[OutreachMessageInputDTO, GenerationResultDTO]
):
    def __init__(self, ai_orchestrator: AICareerAssistantService):
        self._ai = ai_orchestrator

    async def _run(
        self, input_dto: OutreachMessageInputDTO
    ) -> Result[GenerationResultDTO]:
        return await self._ai.generate_content(
            candidate_id=input_dto.candidate_id,
            job_id=input_dto.job_id,
            prompt_id="recruiter_outreach",
            content_type="outreach",
            custom_context={
                "platform": input_dto.platform,
                "recipient": input_dto.recipient_role,
                "company": input_dto.company_name,
            },
        )
