import logging
from typing import Any, Dict

from application.ports.providers.interfaces import IResumeParserProvider
from application.ports.repositories.interfaces import ICandidateRepository
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.profile.entities import Education, Experience, Skill
from domain.shared.enums import SkillCategory
from domain.shared.value_objects import CandidateId, SkillId, SkillLevel

logger = logging.getLogger(__name__)


class ParseResumeUseCase(ApplicationUseCase[tuple, None]):
    """
    Parses raw resume text and populates the Candidate aggregate.
    """

    def __init__(
        self,
        parser_provider: IResumeParserProvider,
        candidate_repo: ICandidateRepository,
        uow: IUnitOfWork,
    ):
        self._parser_provider = parser_provider
        self._candidate_repo = candidate_repo
        self._uow = uow

    async def _run(self, input_data: tuple) -> Result[None]:
        candidate_id_str, raw_text = input_data

        # 1. Dispatch to AI Parser Provider
        parsed_data = await self._parser_provider.parse(raw_text)

        # 2. Load Candidate
        candidate_id = CandidateId.from_str(candidate_id_str)
        candidate = await self._candidate_repo.get_by_id(candidate_id)

        if not candidate:
            return Result.not_found("Candidate not found.")

        # 3. Map Parsed Data to Domain Entities (Manual Mapping for safety)
        # Skills
        for s_data in parsed_data.get("skills", []):
            skill = Skill(
                id=SkillId(),
                name=s_data.get("name"),
                category=SkillCategory(s_data.get("category", "technical")),
                level=SkillLevel(s_data.get("level", 3)),
            )
            candidate.add_skill(skill)

        # Experience
        # (Simplified mapping for this MVP)
        for e_data in parsed_data.get("experience", []):
            from datetime import date

            exp = Experience(
                company_name=e_data.get("company"),
                job_title=e_data.get("title"),
                start_date=date.fromisoformat(e_data.get("start_date", "2000-01-01")),
                end_date=None,  # or parse
            )
            candidate.add_experience(exp)

        # 4. Persist
        async with self._uow:
            await self._candidate_repo.save(candidate)
            await self._uow.commit()

        return Result.ok(None)

    async def execute(self, candidate_id: str, raw_text: str) -> Result[None]:
        return await super().execute((candidate_id, raw_text))
