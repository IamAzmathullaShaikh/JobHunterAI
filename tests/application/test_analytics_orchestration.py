import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.ports.repositories.interfaces import (IApplicationRepository,
                                                       ICandidateRepository)
from application.results.result import Result
from application.services.dashboard_service import DashboardService
from domain.profile.candidate import Candidate
from domain.shared.value_objects import CandidateId, ContactInfo, EmailAddress


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_dashboard_generation_orchestration():
    # 1. Setup Mocks
    c_id = CandidateId()
    mock_candidate = Candidate(
        id=c_id, _full_name="Alex", _contact_info=ContactInfo(EmailAddress("a@b.com"))
    )

    mock_c_repo = MagicMock(spec=ICandidateRepository)
    mock_c_repo.get_by_id = AsyncMock(return_value=mock_candidate)

    mock_app_repo = MagicMock(spec=IApplicationRepository)
    mock_app_repo.list_by_candidate = AsyncMock(return_value=[])

    service = DashboardService(mock_c_repo, mock_app_repo)

    # 2. Run
    res = await service.get_candidate_dashboard(str(c_id))

    # 3. Assert
    assert res.is_success
    assert res.unwrap().conversion_rate == 0.0
    mock_c_repo.get_by_id.assert_called_once()
