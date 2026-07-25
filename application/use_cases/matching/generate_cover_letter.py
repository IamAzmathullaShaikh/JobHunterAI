from application.ports.repositories.interfaces import IResumeRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from core.providers.ai.base import IAIProvider


class GenerateCoverLetterUseCase(ApplicationUseCase[tuple, str]):
    def __init__(self, ai_provider: IAIProvider, resume_repo: IResumeRepository):
        self._ai_provider = ai_provider
        self._resume_repo = resume_repo

    async def _run(self, input_data: tuple) -> Result[str]:
        resume_id, job_description = input_data
        resume = await self._resume_repo.get_by_id(resume_id)
        if not resume:
            return Result.not_found("Resume not found.")

        prompt = f"Write a cover letter for this resume: {resume.current_version.raw_text} and job: {job_description}"

        response = await self._ai_provider.generate(
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.get("data", "Failed to generate.")
        return Result.ok(content)

    async def execute(self, resume_id: str, job_description: str) -> Result[str]:
        return await self._run((resume_id, job_description))
