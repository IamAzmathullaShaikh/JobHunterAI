from application.dto.output.interview_intelligence_output import (
    PreparationPathDTO, StudyPlanDTO)
from application.results.result import Result
from application.use_cases.interview.generate_prep_plan import \
    GeneratePreparationPlanUseCase
from application.use_cases.interview.generate_study_plan import \
    GenerateStudyPlanUseCase


class PreparationWorkflowService:
    def __init__(
        self,
        prep_plan_uc: GeneratePreparationPlanUseCase,
        study_plan_uc: GenerateStudyPlanUseCase,
    ):
        self._prep_plan_uc = prep_plan_uc
        self._study_plan_uc = study_plan_uc

    async def create_full_prep_path(
        self, candidate_id: str, job_id: str
    ) -> Result[PreparationPathDTO]:
        prep_res = await self._prep_plan_uc.execute(candidate_id, job_id)
        study_res = await self._study_plan_uc.execute(candidate_id, job_id)

        if prep_res.is_failure:
            return prep_res
        if study_res.is_failure:
            return study_res

        output = PreparationPathDTO(
            strategy=prep_res.unwrap(), study_plan=study_res.unwrap()
        )

        return Result.ok(output)
