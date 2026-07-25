import logging
import statistics

from application.dto.output.interview_intelligence_output import \
    ReadinessScoreDTO
from application.ports.repositories.interfaces import (ICandidateRepository,
                                                       IJobRepository,
                                                       IResumeRepository)
from application.ports.repositories.interview_repository import \
    IInterviewSessionRepository
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.services.interview.readiness_service import \
    InterviewReadinessService
from domain.services.matching.ats_scoring import ATSScoringService
from domain.services.matching.job_matching import JobMatchingService
from domain.shared.value_objects import CandidateId, JobId

logger = logging.getLogger(__name__)


class CalculateInterviewReadinessUseCase(ApplicationUseCase[tuple, ReadinessScoreDTO]):
    def __init__(
        self,
        candidate_repo: ICandidateRepository,
        job_repo: IJobRepository,
        session_repo: IInterviewSessionRepository,
        resume_repo: IResumeRepository,
    ):
        self._candidate_repo = candidate_repo
        self._job_repo = job_repo
        self._session_repo = session_repo
        self._resume_repo = resume_repo

    async def _run(self, input_data: tuple) -> Result[ReadinessScoreDTO]:
        candidate_id_str, job_id_str = input_data

        c_id = CandidateId.from_str(candidate_id_str)
        candidate = await self._candidate_repo.get_by_id(c_id)
        job = await self._job_repo.get_by_id(JobId.from_str(job_id_str))

        if not candidate or not job:
            return Result.not_found("Entity not found.")

        # 1. Matching Logic
        match = JobMatchingService().calculate_match(candidate, job)

        # 2. ATS logic
        resume = await self._resume_repo.get_latest_for_candidate(c_id)
        if not resume:
            return Result.validation_fail("Candidate has no resume.")
        ats = ATSScoringService.analyze(resume, candidate)

        # 3. Practice logic
        sessions = await self._session_repo.list_by_application(
            job_id_str
        )  # Simple mapping for now
        scores = []
        for s in sessions:
            for a in s.answers:
                if a.star_analysis:
                    scores.append(a.star_analysis.completeness_score)

        avg_practice = statistics.mean(scores) if scores else 0.0

        # 4. Domain Readiness Service
        readiness = InterviewReadinessService.calculate_readiness(
            match, ats, len(sessions), avg_practice
        )

        return Result.ok(
            ReadinessScoreDTO(
                overall=readiness.overall_score,
                is_ready=readiness.is_ready,
                priorities=readiness.improvement_priorities,
                breakdown=readiness.category_scores,
            )
        )

    async def execute(
        self, candidate_id: str, job_id: str
    ) -> Result[ReadinessScoreDTO]:
        return await self._run((candidate_id, job_id))
