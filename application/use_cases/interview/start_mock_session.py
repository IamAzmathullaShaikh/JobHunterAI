import logging

from application.dto.output.interview_intelligence_output import \
    InterviewSessionDTO
from application.ports.repositories.interfaces import (IApplicationRepository,
                                                       ICandidateRepository,
                                                       IJobRepository)
from application.ports.repositories.interview_repository import \
    IInterviewSessionRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.interview.question_service import InterviewQuestionService
from domain.shared.value_objects import (ApplicationId, CandidateId, JobId,
                                         SessionId)
from domain.tracking.interview_entities import InterviewSession

logger = logging.getLogger(__name__)


class StartMockInterviewUseCase(ApplicationUseCase[str, InterviewSessionDTO]):
    def __init__(
        self,
        app_repo: IApplicationRepository,
        candidate_repo: ICandidateRepository,
        job_repo: IJobRepository,
        session_repo: IInterviewSessionRepository,
    ):
        self._app_repo = app_repo
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo
        self._session_repo = session_repo

    async def _run(self, application_id_str: str) -> Result[InterviewSessionDTO]:
        app_id = ApplicationId.from_str(application_id_str)
        application = await self._app_repo.get_by_id(app_id)
        if not application:
            return Result.not_found("Application not found.")

        candidate = await self._candidate_repo.get_by_id(application.candidate_id)
        job = await self._job_repo.get_by_id(application.job_id)

        # 1. Select Questions
        questions = InterviewQuestionService.select_questions(candidate, job)

        # 2. Create Session
        session = InterviewSession(
            id=SessionId(), application_id=app_id, questions=questions
        )

        # 3. Persist
        await self._session_repo.save(session)

        return Result.ok(
            InterviewSessionDTO(
                id=str(session.id),
                application_id=str(session.application_id),
                status=session.status,
                question_count=len(session.questions),
                answer_count=0,
                started_at=session.started_at.isoformat(),
            )
        )

    async def execute(self, application_id: str) -> Result[InterviewSessionDTO]:
        return await self._run(application_id)
