import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.dto.input.job_input import CalculateMatchInputDTO
from application.results.result import Result
from application.services.matching_pipeline import JobMatchingPipelineService
from application.use_cases.matching.generate_ats_report import \
    GenerateATSReportUseCase
from application.use_cases.matching.generate_gap_analysis import \
    GenerateGapAnalysisUseCase
from application.use_cases.matching.match_resume_to_job import \
    MatchResumeToJobUseCase


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_matching_pipeline_success():
    # 1. Setup Mocks
    mock_match = MagicMock(spec=MatchResumeToJobUseCase)
    mock_match.execute = AsyncMock(
        return_value=Result.ok(MagicMock(overall_score=0.85))
    )

    mock_gap = MagicMock(spec=GenerateGapAnalysisUseCase)
    mock_gap.execute = AsyncMock(return_value=Result.ok(MagicMock(job_id="j1")))

    mock_ats = MagicMock(spec=GenerateATSReportUseCase)

    pipeline = JobMatchingPipelineService(
        match_uc=mock_match, gap_uc=mock_gap, ats_uc=mock_ats
    )

    # 2. Run
    res = await pipeline.execute_full_analysis(candidate_id="c1", job_id="j1")

    # 3. Assert
    assert res.is_success
    assert "match" in res.unwrap()
    assert "gaps" in res.unwrap()
    mock_match.execute.assert_called_once()
    mock_gap.execute.assert_called_once()
