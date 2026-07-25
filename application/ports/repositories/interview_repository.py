from abc import ABC, abstractmethod
from typing import List, Optional

from domain.shared.value_objects import CandidateId, SessionId, StudyPlanId
from domain.tracking.interview_entities import InterviewSession, StudyPlan


class IInterviewSessionRepository(ABC):
    @abstractmethod
    async def save(self, session: InterviewSession) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: SessionId) -> Optional[InterviewSession]:
        pass

    @abstractmethod
    async def list_by_application(self, application_id: str) -> List[InterviewSession]:
        pass


class IStudyPlanRepository(ABC):
    @abstractmethod
    async def save(self, plan: StudyPlan) -> None:
        pass

    @abstractmethod
    async def get_latest_for_candidate(
        self, candidate_id: CandidateId
    ) -> Optional[StudyPlan]:
        pass
