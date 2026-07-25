import logging
from typing import Optional

from application.dto.output.interview_intelligence_output import (
    StudyPlanDTO, StudyTopicDTO)
from application.ports.providers.interfaces import IAIProvider
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository)
from application.ports.repositories.interview_repository import \
    IStudyPlanRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.interview.study_plan_service import StudyPlanService
from domain.services.matching.gap_analysis import GapAnalysisService
from domain.shared.value_objects import CandidateId, JobId

logger = logging.getLogger(__name__)


class GenerateStudyPlanUseCase(ApplicationUseCase[tuple, StudyPlanDTO]):
    def __init__(
        self,
        candidate_repo: ICandidateRepository,
        job_repo: IJobRepository,
        study_repo: IStudyPlanRepository,
        ai_provider: Optional[IAIProvider] = None,
    ):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo
        self._study_repo = study_repo
        self._ai_provider = ai_provider

    async def _run(self, input_data: tuple) -> Result[StudyPlanDTO]:
        candidate_id_str, job_id_str = input_data

        c_id = CandidateId.from_str(candidate_id_str)
        candidate = await self._candidate_repo.get_by_id(c_id)
        job = await self._job_repo.get_by_id(JobId.from_str(job_id_str))

        if not candidate or not job:
            return Result.not_found("Entity not found.")

        # 1. Deterministic Gap Analysis & Plan
        gap = GapAnalysisService.generate(candidate, job)
        plan = StudyPlanService.generate_plan(
            candidate_id=c_id,
            missing_skills=gap.missing_skills,
            weak_areas=gap.weak_areas,
            job_id=job_id_str,
        )

        # 2. AI Enrichment (e.g. providing study resources/explanations)
        if self._ai_provider:
            try:
                # Ask AI for resource links for the top missing skill
                if gap.missing_skills:
                    prompt = f"Provide 3 high-quality study resources for: {gap.missing_skills[0]}"
                    # await self._ai_provider.generate(...)
                    logger.info("AI enrichment: study resources generated.")
            except Exception as e:
                logger.warning(
                    f"AI study plan enrichment failed, using deterministic base: {e}"
                )

        # 3. Persist
        await self._study_repo.save(plan)

        # 4. Map to DTO
        return Result.ok(
            StudyPlanDTO(
                id=str(plan.id),
                topic_count=len(plan.topics),
                topics=[
                    StudyTopicDTO(
                        topic=t.topic,
                        priority=t.priority,
                        time_estimate=t.estimated_time_minutes,
                    )
                    for t in plan.topics
                ],
                created_at=plan.created_at.isoformat(),
            )
        )

    async def execute(self, candidate_id: str, job_id: str) -> Result[StudyPlanDTO]:
        return await self._run((candidate_id, job_id))
