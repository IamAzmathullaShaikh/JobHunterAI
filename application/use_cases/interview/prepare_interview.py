from application.ports.repositories.interfaces import IJobRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from core.providers.ai.base import IAIProvider
from domain.shared.value_objects import JobId


class PrepareInterviewUseCase(ApplicationUseCase[str, str]):
    def __init__(self, ai_provider: IAIProvider, job_repo: IJobRepository):
        self._ai_provider = ai_provider
        self._job_repo = job_repo

    async def _run(self, job_id: str) -> Result[str]:
        job = await self._job_repo.get_by_id(JobId.from_str(job_id))
        if not job:
            return Result.not_found("Job not found.")

        prompt = f"Prepare an interview cheat sheet for this job: {job.title} - {job.description}"

        response = await self._ai_provider.generate(
            messages=[{"role": "user", "content": prompt}]
        )

        return Result.ok(response.get("data", "No guide generated."))

    async def execute(self, job_id: str) -> Result[str]:
        return await self._run(job_id)
