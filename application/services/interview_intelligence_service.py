import logging
from typing import List

from application.dto.output.interview_intelligence_output import (
    InterviewPreparationPackageDTO, InterviewQuestionDTO, ReadinessScoreDTO,
    StudyPlanDTO)
from application.results.result import Result
from application.use_cases.interview.calculate_readiness import \
    CalculateInterviewReadinessUseCase
from application.use_cases.interview.generate_questions import \
    GenerateInterviewQuestionsUseCase
from application.use_cases.interview.generate_study_plan import \
    GenerateStudyPlanUseCase

logger = logging.getLogger(__name__)


class InterviewIntelligenceService:
    """
    Coordinator for all interview-related intelligence and preparation workflows.
    """

    def __init__(
        self,
        questions_uc: GenerateInterviewQuestionsUseCase,
        readiness_uc: CalculateInterviewReadinessUseCase,
        study_uc: GenerateStudyPlanUseCase,
    ):
        self._questions_uc = questions_uc
        self._readiness_uc = readiness_uc
        self._study_uc = study_uc

    async def get_preparation_package(
        self, candidate_id: str, job_id: str
    ) -> Result[InterviewPreparationPackageDTO]:
        """
        Aggregates multiple intelligence components into a single preparation package.
        """
        questions_res = await self._questions_uc.execute(candidate_id, job_id)
        readiness_res = await self._readiness_uc.execute(candidate_id, job_id)
        study_res = await self._study_uc.execute(candidate_id, job_id)

        if any(res.is_failure for res in [questions_res, readiness_res, study_res]):
            return Result.business_fail("Failed to compile full preparation package.")

        output = InterviewPreparationPackageDTO(
            questions=questions_res.unwrap(),
            readiness=readiness_res.unwrap(),
            study_plan=study_res.unwrap(),
        )

        return Result.ok(output)
