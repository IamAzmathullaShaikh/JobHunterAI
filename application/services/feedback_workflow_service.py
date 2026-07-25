from application.dto.output.interview_intelligence_output import \
    InterviewFeedbackDTO
from application.results.result import Result
from application.use_cases.interview.analyze_feedback import \
    AnalyzeInterviewFeedbackUseCase


class FeedbackWorkflowService:
    def __init__(self, analyze_uc: AnalyzeInterviewFeedbackUseCase):
        self._analyze_uc = analyze_uc

    async def get_session_insights(
        self, session_id: str
    ) -> Result[InterviewFeedbackDTO]:
        return await self._analyze_uc.execute(session_id)
