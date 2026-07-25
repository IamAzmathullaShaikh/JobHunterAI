from application.dto.input.resume_input import (AnalyzeResumeInputDTO,
                                                ResumeUploadInputDTO)
from application.dto.output.resume_output import ResumeOutputDTO
from application.results.result import Result
from application.use_cases.resume.analyze_resume import AnalyzeResumeUseCase
from application.use_cases.resume.upload_resume import UploadResumeUseCase


class ResumeApplicationService:
    """Orchestrates resume-related workflows."""

    def __init__(
        self, upload_uc: UploadResumeUseCase, analyze_uc: AnalyzeResumeUseCase
    ):
        self._upload_uc = upload_uc
        self._analyze_uc = analyze_uc

    async def upload_and_analyze(
        self, upload_dto: ResumeUploadInputDTO
    ) -> Result[ResumeOutputDTO]:
        upload_res = await self._upload_uc.execute(upload_dto)
        if upload_res.is_failure:
            return upload_res

        analyze_dto = AnalyzeResumeInputDTO(resume_id=upload_res.value.id)
        # Chain but keep original result for return or merge
        await self._analyze_uc.execute(analyze_dto)

        return upload_res
