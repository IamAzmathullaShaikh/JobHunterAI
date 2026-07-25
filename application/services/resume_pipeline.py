import logging

from application.dto.input.resume_input import (AnalyzeResumeInputDTO,
                                                ResumeUploadInputDTO)
from application.dto.output.resume_output import ResumeAnalysisOutputDTO
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.resume.analyze_resume import AnalyzeResumeUseCase
from application.use_cases.resume.extract_text import ExtractResumeTextUseCase
from application.use_cases.resume.parse_resume import ParseResumeUseCase
from application.use_cases.resume.upload_resume import UploadResumeUseCase

logger = logging.getLogger(__name__)


class ResumePipelineService:
    """
    Coordinates the end-to-end Resume Intelligence Pipeline.
    Upload -> Extract -> Parse -> Analyze
    """

    def __init__(
        self,
        upload_uc: UploadResumeUseCase,
        extract_uc: ExtractResumeTextUseCase,
        parse_uc: ParseResumeUseCase,
        analyze_uc: AnalyzeResumeUseCase,
        uow: IUnitOfWork,
    ):
        self._upload_uc = upload_uc
        self._extract_uc = extract_uc
        self._parse_uc = parse_uc
        self._analyze_uc = analyze_uc
        self._uow = uow

    async def run_full_pipeline(
        self, upload_dto: ResumeUploadInputDTO
    ) -> Result[ResumeAnalysisOutputDTO]:
        logger.info(
            f"Starting full intelligence pipeline for file: {upload_dto.filename}"
        )

        # 1. Upload & Store
        upload_res = await self._upload_uc.execute(upload_dto)
        if upload_res.is_failure:
            return upload_res

        resume_id = upload_res.unwrap().id

        # 2. Extract Text
        extract_res = await self._extract_uc.execute(
            upload_dto.file_content, upload_dto.content_type
        )
        if extract_res.is_failure:
            return extract_res

        raw_text = extract_res.unwrap()

        # 3. Parse and Populate Domain (Update Candidate Aggregate)
        parse_res = await self._parse_uc.execute(upload_dto.candidate_id, raw_text)
        if parse_res.is_failure:
            return parse_res

        # 4. Perform Quality Analysis
        analyze_dto = AnalyzeResumeInputDTO(resume_id=resume_id)
        return await self._analyze_uc.execute(analyze_dto)
