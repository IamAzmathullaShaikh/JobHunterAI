import logging

from application.dto.output.interview_intelligence_output import \
    STARAnalysisDTO
from application.ports.repositories.interview_repository import \
    IInterviewSessionRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.interview.star_coaching import STARCoachingService
from domain.shared.value_objects import QuestionId, SessionId

logger = logging.getLogger(__name__)


class EvaluateInterviewAnswerUseCase(ApplicationUseCase[tuple, STARAnalysisDTO]):
    def __init__(self, session_repo: IInterviewSessionRepository):
        self._session_repo = session_repo

    async def _run(self, input_data: tuple) -> Result[STARAnalysisDTO]:
        session_id_str, question_id_str, answer_text = input_data

        session = await self._session_repo.get_by_id(SessionId.from_str(session_id_str))
        if not session:
            return Result.not_found("Session not found.")

        # 1. Domain Coaching Logic
        analysis = STARCoachingService.analyze_answer(answer_text)

        # 2. Record in Session
        session.record_answer(
            QuestionId.from_str(question_id_str), answer_text, analysis
        )

        # 3. Persist
        await self._session_repo.save(session)

        # 4. Map to DTO
        return Result.ok(
            STARAnalysisDTO(
                score=analysis.completeness_score,
                feedback=analysis.feedback,
                missing_components=[
                    k
                    for k, v in {
                        "Situation": analysis.has_situation,
                        "Task": analysis.has_task,
                        "Action": analysis.has_action,
                        "Result": analysis.has_result,
                    }.items()
                    if not v
                ],
                suggestions=analysis.suggestions,
            )
        )

    async def execute(
        self, session_id: str, question_id: str, answer_text: str
    ) -> Result[STARAnalysisDTO]:
        return await self._run((session_id, question_id, answer_text))
