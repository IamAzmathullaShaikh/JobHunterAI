from datetime import datetime

from application.dto.output.analytics_output import (DashboardDTO,
                                                     ExecutiveSummaryDTO)
from application.results.result import Result
from application.services.ai_career_assistant_service import \
    AICareerAssistantService
from application.use_cases.base import ApplicationUseCase


class GenerateExecutiveSummaryUseCase(
    ApplicationUseCase[DashboardDTO, ExecutiveSummaryDTO]
):
    def __init__(self, ai_assistant: AICareerAssistantService):
        self._ai = ai_assistant

    async def _run(self, dashboard: DashboardDTO) -> Result[ExecutiveSummaryDTO]:
        # We use a placeholder candidate_id for the context of this summary
        # or we could extract it from the dashboard context if available.
        # For the MVP, we assume the AI can process the flattened dashboard stats.

        prompt_context = {
            "kpis": dashboard.kpis,
            "funnel": dashboard.funnel,
            "top_recommendation": (
                dashboard.recommendations[0].message
                if dashboard.recommendations
                else "N/A"
            ),
        }

        # Call AI Orchestrator
        ai_res = await self._ai.generate_content(
            candidate_id="system",  # Summary context
            prompt_id="executive_summary",
            custom_context=prompt_context,
            content_type="report",
        )

        if ai_res.is_failure:
            return Result.ok(
                ExecutiveSummaryDTO(
                    content="Standard summary: Your job search is progressing. Review your recommendations for details.",
                    generated_at=datetime.now().isoformat(),
                    is_ai_generated=False,
                )
            )

        return Result.ok(
            ExecutiveSummaryDTO(
                content=ai_res.unwrap().content,
                generated_at=datetime.now().isoformat(),
                is_ai_generated=not ai_res.unwrap().metadata.is_fallback,
            )
        )
