import logging

from application.dto.output.interview_intelligence_output import \
    InterviewFeedbackDTO
from application.ports.repositories.interview_repository import \
    IInterviewSessionRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.interview.feedback_analysis import FeedbackAnalysisService
from domain.shared.value_objects import SessionId

logger = logging.getLogger(__name__)


class AnalyzeInterviewFeedbackUseCase(ApplicationUseCase[str, InterviewFeedbackDTO]):
    def __init__(self, session_repo: IInterviewSessionRepository):
        self._session_repo = session_repo

    async def _run(self, session_id_str: str) -> Result[InterviewFeedbackDTO]:
        session = await self._session_repo.get_by_id(SessionId.from_str(session_id_str))
        if not session:
            return Result.not_found("Session not found.")

        analysis = FeedbackAnalysisService.analyze_session(session)

        output = InterviewFeedbackDTO(
            average_star_score=analysis.get("average_star_score", 0.0),
            critical_gaps=analysis.get("critical_gaps", []),
            overall_sentiment=analysis.get("overall_sentiment", "Unknown"),
        )

        return Result.ok(output)

    async def execute(self, session_id: str) -> Result[InterviewFeedbackDTO]:
        return await self._run(session_id)
