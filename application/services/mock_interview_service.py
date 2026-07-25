from application.dto.output.interview_intelligence_output import (
    InterviewSessionDTO, STARAnalysisDTO)
from application.results.result import Result
from application.use_cases.interview.evaluate_answer import \
    EvaluateInterviewAnswerUseCase
from application.use_cases.interview.generate_summary import \
    GenerateInterviewSummaryUseCase
from application.use_cases.interview.start_mock_session import \
    StartMockInterviewUseCase


class MockInterviewService:
    def __init__(
        self,
        start_uc: StartMockInterviewUseCase,
        evaluate_uc: EvaluateInterviewAnswerUseCase,
        summary_uc: GenerateInterviewSummaryUseCase,
    ):
        self._start_uc = start_uc
        self._evaluate_uc = evaluate_uc
        self._summary_uc = summary_uc

    async def begin_session(self, application_id: str) -> Result[InterviewSessionDTO]:
        return await self._start_uc.execute(application_id)

    async def submit_answer(
        self, session_id: str, question_id: str, text: str
    ) -> Result[STARAnalysisDTO]:
        return await self._evaluate_uc.execute(session_id, question_id, text)

    async def get_summary(self, session_id: str) -> Result[str]:
        return await self._summary_uc.execute(session_id)
