import logging

from application.ports.providers.matching_providers import IJobParserProvider
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.discovery.entities import JobDescription, JobRequirement

logger = logging.getLogger(__name__)


class ParseJobUseCase(ApplicationUseCase[str, JobDescription]):
    """
    Orchestrates parsing a raw job description into structured domain requirements.
    """

    def __init__(self, parser_provider: IJobParserProvider):
        self._parser_provider = parser_provider

    async def _run(self, raw_text: str) -> Result[JobDescription]:
        try:
            # 1. Dispatch to Provider
            parsed_data = await self._parser_provider.parse_job(raw_text)

            # 2. Map to Domain
            requirements = []
            for req in parsed_data.get("requirements", []):
                requirements.append(
                    JobRequirement(
                        name=req.get("name"),
                        is_required=req.get("is_required", True),
                        category=req.get("category", "general"),
                    )
                )

            job_desc = JobDescription(raw_text=raw_text, requirements=requirements)

            return Result.ok(job_desc)

        except Exception as e:
            logger.error(f"Job parsing failed: {e}")
            return Result.infra_fail(str(e))
