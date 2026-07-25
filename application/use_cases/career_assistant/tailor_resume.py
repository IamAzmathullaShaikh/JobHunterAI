from application.dto.input.career_assistant_input import \
    ResumeTailoringInputDTO
from application.dto.output.career_assistant_output import GenerationResultDTO
from application.results.result import Result
from application.services.ai_career_assistant_service import \
    AICareerAssistantService
from application.use_cases.base import ApplicationUseCase


class GenerateTailoredResumeUseCase(
    ApplicationUseCase[ResumeTailoringInputDTO, GenerationResultDTO]
):
    def __init__(self, ai_orchestrator: AICareerAssistantService):
        self._ai = ai_orchestrator

    async def _run(
        self, input_dto: ResumeTailoringInputDTO
    ) -> Result[GenerationResultDTO]:
        return await self._ai.generate_content(
            candidate_id=input_dto.candidate_id,
            job_id=input_dto.job_id,
            prompt_id="resume_tailoring",
            content_type="resume",
            custom_context={
                "target_role": input_dto.target_role,
                "focus_skills": input_dto.focus_skills,
            },
        )
