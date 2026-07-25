import logging
from typing import Any, Dict, List

from application.dto.input.job_input import CalculateMatchInputDTO
from application.dto.output.matching_output import (ATSReportDTO, GapReportDTO,
                                                    JobMatchDTO)
from application.results.result import Result
from application.use_cases.matching.generate_ats_report import \
    GenerateATSReportUseCase
from application.use_cases.matching.generate_gap_analysis import \
    GenerateGapAnalysisUseCase
from application.use_cases.matching.match_resume_to_job import \
    MatchResumeToJobUseCase

logger = logging.getLogger(__name__)


class JobMatchingPipelineService:
    """
    Orchestrates the flow from resume to a complete job-match intelligence report.
    """

    def __init__(
        self,
        match_uc: MatchResumeToJobUseCase,
        gap_uc: GenerateGapAnalysisUseCase,
        ats_uc: GenerateATSReportUseCase,
    ):
        self._match_uc = match_uc
        self._gap_uc = gap_uc
        self._ats_uc = ats_uc

    async def execute_full_analysis(
        self, candidate_id: str, job_id: str
    ) -> Result[Dict[str, Any]]:
        """
        Runs the full intelligence pipeline for a specific candidate-job pair.
        """
        input_dto = CalculateMatchInputDTO(candidate_id=candidate_id, job_id=job_id)

        # 1. Basic Matching
        match_res = await self._match_uc.execute(input_dto)
        if match_res.is_failure:
            return match_res

        # 2. Gap Analysis
        gap_res = await self._gap_uc.execute(input_dto)
        if gap_res.is_failure:
            return gap_res

        # 3. Resume analysis (Latest resume for candidate)
        # Note: In a real app we'd need the resume_id
        # For simplicity, we'll assume we have a way to get it or skip if not available

        return Result.ok({"match": match_res.unwrap(), "gaps": gap_res.unwrap()})
