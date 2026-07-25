import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.dto.input.candidate_input import CreateCandidateInputDTO
from application.ports.repositories.interfaces import ICandidateRepository
from application.ports.unit_of_work import IUnitOfWork
from application.use_cases.candidate.create_candidate import \
    CreateCandidateUseCase


def async_test(f):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


@async_test
async def test_create_candidate_use_case():
    # 1. Setup Mocks
    mock_repo = MagicMock(spec=ICandidateRepository)
    mock_repo.find_by_email = AsyncMock(return_value=None)
    mock_repo.save = AsyncMock()

    mock_uow = MagicMock(spec=IUnitOfWork)
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=None)
    mock_uow.commit = AsyncMock()

    uc = CreateCandidateUseCase(mock_repo, mock_uow)

    # 2. Execute
    input_dto = CreateCandidateInputDTO(
        full_name="Alex Test", email="alex@test.com", phone="+1234567890"
    )

    result = await uc.execute(input_dto)

    # 3. Verify
    assert result.is_success
    assert result.value.full_name == "Alex Test"
    mock_repo.save.assert_called_once()
    mock_uow.commit.assert_called_once()


@async_test
async def test_create_candidate_duplicate_email():
    mock_repo = MagicMock(spec=ICandidateRepository)
    mock_repo.find_by_email = AsyncMock(return_value=MagicMock())

    mock_uow = MagicMock(spec=IUnitOfWork)

    uc = CreateCandidateUseCase(mock_repo, mock_uow)

    input_dto = CreateCandidateInputDTO(full_name="Alex Test", email="exists@test.com")

    result = await uc.execute(input_dto)

    assert result.is_failure
    assert "already exists" in result.failure.message
