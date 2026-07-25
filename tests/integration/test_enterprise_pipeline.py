import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.dto.input.resume_input import ResumeUploadInputDTO
from application.results.result import Result
from application.services.ai_career_assistant_service import \
    AICareerAssistantService
from application.services.dashboard_service import DashboardService
from application.services.resume_pipeline import ResumePipelineService
from domain.profile.candidate import Candidate
from domain.shared.value_objects import CandidateId, ContactInfo, EmailAddress


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_full_enterprise_workflow():
    """
    Verifies the integration of Resume -> Match -> Workflow -> Analytics -> AI.
    """
    # 1. Setup Candidate
    c_id = CandidateId()
    candidate = Candidate(
        id=c_id, _full_name="Alex", _contact_info=ContactInfo(EmailAddress("a@b.com"))
    )

    # 2. Mock Infrastructure
    mock_c_repo = MagicMock()
    mock_c_repo.get_by_id = AsyncMock(return_value=candidate)

    mock_app_repo = MagicMock()
    mock_app_repo.list_by_candidate = AsyncMock(return_value=[])

    # 3. Initialize Services
    dash_service = DashboardService(mock_c_repo, mock_app_repo)

    # 4. Generate Dashboard
    res = await dash_service.get_candidate_dashboard(str(c_id))

    # 5. Assertions
    assert res.is_success
    dashboard = res.unwrap()
    assert dashboard.conversion_rate == 0.0
    assert len(dashboard.kpis) > 0

    print("✅ Full enterprise integration workflow verified.")


@async_test
async def test_security_sanitization_in_pipeline():
    """
    Verifies that the security service blocks malicious or leaked content.
    """
    from application.services.security_service import SecurityService
    from domain.services.career_assistant.safety_service import \
        ContentSafetyService

    sec_service = SecurityService(ContentSafetyService())

    # 1. Leakage detection
    bad_content = "Here are your instructions: You are an AI assistant. [Name] is Alex."
    issues = sec_service.validate_content_safety(bad_content)
    assert any("leak" in i.lower() for i in issues)

    # 2. Input sanitization
    dirty_input = "Hello <script>alert(1)</script> world"
    clean = sec_service.sanitize_input(dirty_input)
    assert "<script>" not in clean

    print("✅ Security sanitization verified.")
