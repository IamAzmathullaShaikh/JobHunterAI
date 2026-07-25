import logging

from application.dto.output.interview_intelligence_output import \
    InterviewSummaryDTO
from application.ports.repositories.interview_repository import \
    IInterviewSessionRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.value_objects import SessionId

logger = logging.getLogger(__name__)


class GenerateInterviewSummaryUseCase(ApplicationUseCase[str, InterviewSummaryDTO]):
    def __init__(self, session_repo: IInterviewSessionRepository):
        self._session_repo = session_repo

    async def _run(self, session_id_str: str) -> Result[InterviewSummaryDTO]:
        session = await self._session_repo.get_by_id(SessionId.from_str(session_id_str))
        if not session:
            return Result.not_found("Session not found.")

        # Deterministic Summary
        summary_text = f"Mock Interview Session Summary\n"
        summary_text += f"Status: {session.status}\n"
        summary_text += f"Questions: {len(session.questions)}\n"
        summary_text += f"Answers Recorded: {len(session.answers)}\n"

        completion_rate = (
            len(session.answers) / len(session.questions) if session.questions else 0.0
        )

        output = InterviewSummaryDTO(
            session_id=str(session.id),
            status=session.status,
            summary_text=summary_text,
            completion_rate=round(completion_rate, 2),
        )

        return Result.ok(output)

    async def execute(self, session_id: str) -> Result[InterviewSummaryDTO]:
        return await self._run(session_id)
