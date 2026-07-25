import logging

from application.dto.output.interview_intelligence_output import \
    CompanyInsightsDTO
from application.ports.providers.company_intel import ICompanyKnowledgeProvider
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase

logger = logging.getLogger(__name__)


class GenerateCompanyInsightsUseCase(ApplicationUseCase[str, CompanyInsightsDTO]):
    """
    Retrieves AI-enriched company research and culture insights.
    """

    def __init__(self, provider: ICompanyKnowledgeProvider):
        self._provider = provider

    async def _run(self, company_name: str) -> Result[CompanyInsightsDTO]:
        try:
            intel = await self._provider.get_company_profile(company_name)

            output = CompanyInsightsDTO(
                company_name=company_name,
                overview=intel.get("overview", "No overview available."),
                culture_themes=intel.get("culture_themes", []),
                tech_stack=intel.get("tech_stack", []),
                likely_interview_questions=intel.get("likely_questions", []),
            )

            return Result.ok(output)

        except Exception as e:
            logger.error(f"Company intel extraction failed: {e}")
            return Result.infra_fail(str(e))

    async def execute(self, company_name: str) -> Result[CompanyInsightsDTO]:
        return await self._run(company_name)
