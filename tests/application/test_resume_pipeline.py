import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.dto.input.resume_input import ResumeUploadInputDTO
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.services.resume_pipeline import ResumePipelineService
from application.use_cases.resume.analyze_resume import AnalyzeResumeUseCase
from application.use_cases.resume.extract_text import ExtractResumeTextUseCase
from application.use_cases.resume.parse_resume import ParseResumeUseCase
from application.use_cases.resume.upload_resume import UploadResumeUseCase


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_full_resume_pipeline_success():
    # 1. Mocks
    mock_upload = MagicMock(spec=UploadResumeUseCase)
    mock_upload.execute = AsyncMock(return_value=Result.ok(MagicMock(id="r1")))

    mock_extract = MagicMock(spec=ExtractResumeTextUseCase)
    mock_extract.execute = AsyncMock(return_value=Result.ok("raw text content"))

    mock_parse = MagicMock(spec=ParseResumeUseCase)
    mock_parse.execute = AsyncMock(return_value=Result.ok(None))

    mock_analyze = MagicMock(spec=AnalyzeResumeUseCase)
    mock_analyze.execute = AsyncMock(
        return_value=Result.ok(MagicMock(resume_id="r1", strengths=[]))
    )

    mock_uow = MagicMock(spec=IUnitOfWork)

    pipeline = ResumePipelineService(
        upload_uc=mock_upload,
        extract_uc=mock_extract,
        parse_uc=mock_parse,
        analyze_uc=mock_analyze,
        uow=mock_uow,
    )

    # 2. Input
    dto = ResumeUploadInputDTO(
        candidate_id="c1",
        file_content=b"pdf_bytes",
        filename="cv.pdf",
        content_type="application/pdf",
    )

    # 3. Run
    result = await pipeline.run_full_pipeline(dto)

    # 4. Assert
    assert result.is_success
    mock_upload.execute.assert_called_once()
    mock_extract.execute.assert_called_once()
    mock_parse.execute.assert_called_once()
    mock_analyze.execute.assert_called_once()
