from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from domain.discovery.company import Company
from domain.discovery.entities import Job
from domain.profile.candidate import Candidate
from domain.profile.entities import Resume
from domain.shared.value_objects import (ApplicationId, CandidateId, CompanyId,
                                         JobId)
from domain.tracking.application import Application

T = TypeVar("T")
ID = TypeVar("ID")


class IRepository(ABC, Generic[T, ID]):
    """Generic repository contract for all domain aggregates."""

    @abstractmethod
    async def save(self, entity: T) -> None:
        pass

    @abstractmethod
    async def update(self, entity: T) -> None:
        pass

    @abstractmethod
    async def delete(self, id: ID) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        pass

    @abstractmethod
    async def exists(self, id: ID) -> bool:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass


class ICandidateRepository(IRepository[Candidate, CandidateId]):
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Candidate]:
        pass


class IResumeRepository(IRepository[Resume, str]):  # String for now or ResumeId
    @abstractmethod
    async def get_latest_for_candidate(
        self, candidate_id: CandidateId
    ) -> Optional[Resume]:
        pass


class IJobRepository(IRepository[Job, JobId]):
    @abstractmethod
    async def list_active(self, limit: int, offset: int = 0) -> List[Job]:
        pass

    @abstractmethod
    async def search(self, query: str) -> List[Job]:
        pass


class ICompanyRepository(IRepository[Company, CompanyId]):
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Company]:
        pass


class IApplicationRepository(IRepository[Application, ApplicationId]):
    @abstractmethod
    async def list_by_candidate(self, candidate_id: CandidateId) -> List[Application]:
        pass

    @abstractmethod
    async def list_by_job(self, job_id: JobId) -> List[Application]:
        pass
