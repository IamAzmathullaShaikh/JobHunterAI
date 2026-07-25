from application.dto.input.resume_input import AnalyzeResumeInputDTO
from application.dto.output.resume_output import ResumeAnalysisOutputDTO
from application.results.result import Result
from application.use_cases.resume.analyze_resume import AnalyzeResumeUseCase


class ResumeAnalysisService:
    def __init__(self, analyze_uc: AnalyzeResumeUseCase):
        self._analyze_uc = analyze_uc

    async def get_comprehensive_analysis(
        self, resume_id: str
    ) -> Result[ResumeAnalysisOutputDTO]:
        dto = AnalyzeResumeInputDTO(resume_id=resume_id)
        return await self._analyze_uc.execute(dto)
