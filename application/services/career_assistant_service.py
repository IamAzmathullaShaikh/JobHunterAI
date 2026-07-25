from application.dto.input.career_assistant_input import (
    BaseGenerationInputDTO, CareerAdviceInputDTO, CoverLetterInputDTO,
    OutreachMessageInputDTO, ResumeTailoringInputDTO)
from application.dto.output.career_assistant_output import GenerationResultDTO
from application.results.result import Result
from application.use_cases.career_assistant.application_follow_up import \
    GenerateFollowUpEmailUseCase
from application.use_cases.career_assistant.career_advice import \
    GenerateCareerAdviceUseCase
from application.use_cases.career_assistant.generate_cover_letter import \
    GenerateCoverLetterUseCase
from application.use_cases.career_assistant.interview_thank_you import \
    GenerateInterviewThankYouUseCase
from application.use_cases.career_assistant.linkedin_optimizer import \
    GenerateLinkedInProfileUseCase
from application.use_cases.career_assistant.networking_message import \
    GenerateNetworkingMessageUseCase
from application.use_cases.career_assistant.recruiter_message import \
    GenerateRecruiterMessageUseCase
from application.use_cases.career_assistant.salary_negotiation import \
    GenerateSalaryNegotiationGuideUseCase
from application.use_cases.career_assistant.tailor_resume import \
    GenerateTailoredResumeUseCase


class CareerAssistantService:
    """
    Top-level application service that aggregates all AI career assistance use cases.
    """

    def __init__(
        self,
        tailor_resume_uc: GenerateTailoredResumeUseCase,
        cover_letter_uc: GenerateCoverLetterUseCase,
        recruiter_msg_uc: GenerateRecruiterMessageUseCase,
        career_advice_uc: GenerateCareerAdviceUseCase,
        linkedin_uc: GenerateLinkedInProfileUseCase,
        networking_uc: GenerateNetworkingMessageUseCase,
        thank_you_uc: GenerateInterviewThankYouUseCase,
        follow_up_uc: GenerateFollowUpEmailUseCase,
        salary_uc: GenerateSalaryNegotiationGuideUseCase,
    ):
        self._tailor_resume_uc = tailor_resume_uc
        self._cover_letter_uc = cover_letter_uc
        self._recruiter_msg_uc = recruiter_msg_uc
        self._career_advice_uc = career_advice_uc
        self._linkedin_uc = linkedin_uc
        self._networking_uc = networking_uc
        self._thank_you_uc = thank_you_uc
        self._follow_up_uc = follow_up_uc
        self._salary_uc = salary_uc

    async def tailor_resume(
        self, dto: ResumeTailoringInputDTO
    ) -> Result[GenerationResultDTO]:
        return await self._tailor_resume_uc.execute(dto)

    async def generate_cover_letter(
        self, dto: CoverLetterInputDTO
    ) -> Result[GenerationResultDTO]:
        return await self._cover_letter_uc.execute(dto)

    async def draft_recruiter_message(
        self, dto: OutreachMessageInputDTO
    ) -> Result[GenerationResultDTO]:
        return await self._recruiter_msg_uc.execute(dto)

    async def get_career_guidance(
        self, dto: CareerAdviceInputDTO
    ) -> Result[GenerationResultDTO]:
        return await self._career_advice_uc.execute(dto)

    async def optimize_linkedin(self, candidate_id: str) -> Result[GenerationResultDTO]:
        return await self._linkedin_uc.execute(
            BaseGenerationInputDTO(candidate_id=candidate_id)
        )

    async def draft_networking_message(
        self, candidate_id: str
    ) -> Result[GenerationResultDTO]:
        return await self._networking_uc.execute(
            BaseGenerationInputDTO(candidate_id=candidate_id)
        )

    async def draft_thank_you_email(
        self, candidate_id: str, job_id: str
    ) -> Result[GenerationResultDTO]:
        return await self._thank_you_uc.execute(
            BaseGenerationInputDTO(candidate_id=candidate_id, job_id=job_id)
        )

    async def draft_follow_up(
        self, candidate_id: str, job_id: str
    ) -> Result[GenerationResultDTO]:
        return await self._follow_up_uc.execute(
            BaseGenerationInputDTO(candidate_id=candidate_id, job_id=job_id)
        )

    async def get_salary_negotiation_guide(
        self, candidate_id: str, job_id: str
    ) -> Result[GenerationResultDTO]:
        return await self._salary_uc.execute(
            BaseGenerationInputDTO(candidate_id=candidate_id, job_id=job_id)
        )
