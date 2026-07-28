from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.container import container
from core.database.connection import get_db_session
from core.enricher import Enricher
from core.providers.circuit_breaker import CircuitBreaker
from core.providers.manager import ProviderManager
from core.providers.registry import ProviderRegistry
from core.providers.telemetry import TelemetryEngine
from core.resume_engine import ResumeEngine
from core.services.job_service import JobService
from core.services.resume_service import ResumeService
from core.services.interview_service import InterviewService
from core.services.generator_service import GeneratorService


from typing import Optional
from uuid import UUID


# --- Infrastructure Dependencies ---


def get_current_user_id() -> Optional[UUID]:
    """
    Placeholder for future Auth integration.
    Currently returns a static UUID for single-user mode.
    """
    return UUID("00000000-0000-0000-0000-000000000000")


def get_container() -> container:
    return container


def get_settings():
    return container.settings


def get_registry() -> ProviderRegistry:
    return container.registry


def get_provider_manager() -> ProviderManager:
    return container.provider_manager


def get_circuit_breaker() -> CircuitBreaker:
    return container.circuit_breaker


def get_telemetry_engine() -> TelemetryEngine:
    return container.telemetry_engine


# --- Service Dependencies ---


async def get_job_service(db: AsyncSession = Depends(get_db_session)) -> JobService:
    return JobService(db)


async def get_resume_service(db: AsyncSession = Depends(get_db_session)) -> ResumeService:
    return ResumeService(db)


async def get_interview_service(db: AsyncSession = Depends(get_db_session)) -> InterviewService:
    return InterviewService(db)


async def get_generator_service(db: AsyncSession = Depends(get_db_session)) -> GeneratorService:
    return GeneratorService(db)


async def get_resume_engine() -> ResumeEngine:
    return ResumeEngine()


async def get_enricher() -> Enricher:
    return Enricher()
