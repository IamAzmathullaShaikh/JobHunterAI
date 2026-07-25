from application.dto.input.resume_input import AnalyzeResumeInputDTO
from application.dto.output.resume_output import ResumeAnalysisOutputDTO
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from application.use_cases.resume.get_analysis import GetResumeAnalysisUseCase


class AnalyzeResumeUseCase(
    ApplicationUseCase[AnalyzeResumeInputDTO, ResumeAnalysisOutputDTO]
):
    """
    Application-level orchestration for resume analysis.
    """

    def __init__(self, get_analysis_uc: GetResumeAnalysisUseCase):
        self._get_analysis_uc = get_analysis_uc

    async def _run(
        self, input_dto: AnalyzeResumeInputDTO
    ) -> Result[ResumeAnalysisOutputDTO]:
        return await self._get_analysis_uc.execute(input_dto.resume_id)
