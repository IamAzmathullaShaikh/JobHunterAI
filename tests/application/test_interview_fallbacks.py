import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from application.use_cases.interview.generate_questions import \
    GenerateInterviewQuestionsUseCase
from core.providers.ai.base import IAIProvider
from domain.discovery.entities import Job, Location
from domain.profile.candidate import Candidate
from domain.shared.value_objects import CandidateId, JobId


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_question_generation_fallback():
    # 1. Setup Data
    c_id = CandidateId()
    j_id = JobId()

    mock_candidate = MagicMock(spec=Candidate)
    mock_candidate.id = c_id
    mock_candidate.skills = []

    mock_job = MagicMock(spec=Job)
    mock_job.id = j_id
    mock_job.required_skills = ["Python"]
    mock_job.company_id = "TechCo"
    mock_job.experience_level = None

    mock_c_repo = MagicMock(spec=ICandidateRepository)
    mock_c_repo.get_by_id = AsyncMock(return_value=mock_candidate)

    mock_j_repo = MagicMock(spec=IJobRepository)
    mock_j_repo.get_by_id = AsyncMock(return_value=mock_job)

    # AI provider that always fails
    mock_ai = MagicMock(spec=IAIProvider)
    mock_ai.generate = AsyncMock(side_effect=RuntimeError("AI Down"))

    uc = GenerateInterviewQuestionsUseCase(mock_c_repo, mock_j_repo, mock_ai)

    # 2. Run
    res = await uc.execute(str(c_id), str(j_id))

    # 3. Assert - Should still succeed with deterministic questions
    assert res.is_success
    assert len(res.unwrap()) > 0
    assert any("Python" in q.text for q in res.unwrap())
