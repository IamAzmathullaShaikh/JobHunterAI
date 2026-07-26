import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.dto.input.application_input import CreateApplicationInputDTO
from application.ports.repositories.interfaces import IApplicationRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.application.submit_application import \
    SubmitApplicationUseCase
from domain.shared.enums import ApplicationStatus
from domain.shared.value_objects import ApplicationId, CandidateId, JobId
from domain.tracking.application import Application


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_submit_application_orchestration():
    # 1. Setup Mocks
    app_id = ApplicationId()
    # Create a real domain object for state machine testing
    app = Application(id=app_id, candidate_id=CandidateId(), job_id=JobId())

    mock_repo = MagicMock(spec=IApplicationRepository)
    mock_repo.get_by_id = AsyncMock(return_value=app)
    mock_repo.save = AsyncMock()

    mock_uow = MagicMock(spec=IUnitOfWork)
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.commit = AsyncMock()

    uc = SubmitApplicationUseCase(mock_repo, mock_uow)

    # 2. Run
    res = await uc.execute(str(app_id))

    # 3. Assert
    assert res.is_success
    assert app.status == ApplicationStatus.APPLIED
    assert len(app.history) > 0
    mock_repo.save.assert_called_once()
