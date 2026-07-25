import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.ports.repositories.interview_repository import \
    IInterviewSessionRepository
from application.use_cases.interview.evaluate_answer import \
    EvaluateInterviewAnswerUseCase
from domain.shared.value_objects import ApplicationId, QuestionId, SessionId
from domain.tracking.interview_entities import InterviewSession


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_evaluate_answer_flow():
    # 1. Setup Mocks
    session_id = SessionId()
    session = InterviewSession(
        id=session_id, application_id=ApplicationId(), questions=[]
    )

    mock_repo = MagicMock(spec=IInterviewSessionRepository)
    mock_repo.get_by_id = AsyncMock(return_value=session)
    mock_repo.save = AsyncMock()

    uc = EvaluateInterviewAnswerUseCase(mock_repo)

    # 2. Run
    res = await uc.execute(
        session_id=str(session_id),
        question_id=str(QuestionId()),
        answer_text="When I was at work I implemented a fix that saved time.",
    )

    # 3. Assert
    assert res.is_success
    assert res.unwrap().score > 0
    mock_repo.save.assert_called_once()
    assert len(session.answers) == 1
