import logging

from application.dto.input.resume_input import ResumeUploadInputDTO
from application.dto.output.resume_output import ResumeOutputDTO
from application.mappers.resume_mapper import ResumeMapper
from application.ports.repositories.interfaces import ICandidateRepository
from application.ports.storage.interfaces import IFileStorage
from application.ports.unit_of_work import IUnitOfWork
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.value_objects import CandidateId, ResumeId, ResumeVersionId

logger = logging.getLogger(__name__)


class UploadResumeUseCase(ApplicationUseCase[ResumeUploadInputDTO, ResumeOutputDTO]):
    """
    Handles the physical upload and persistence of a resume file.
    """

    def __init__(
        self,
        candidate_repo: ICandidateRepository,
        storage: IFileStorage,
        uow: IUnitOfWork,
    ):
        self._candidate_repo = candidate_repo
        self._storage = storage
        self._uow = uow

    async def _run(self, input_dto: ResumeUploadInputDTO) -> Result[ResumeOutputDTO]:
        # 1. Load Candidate
        candidate = await self._candidate_repo.get_by_id(
            CandidateId.from_str(input_dto.candidate_id)
        )
        if not candidate:
            return Result.not_found(f"Candidate {input_dto.candidate_id} not found.")

        # 2. Save to Storage
        try:
            file_uri = await self._storage.save(
                input_dto.file_content, input_dto.filename, input_dto.content_type
            )
        except Exception as e:
            return Result.infra_fail(f"Storage failure: {str(e)}")

        # 3. Domain behavior (Add to aggregate)
        resume = candidate.add_resume(
            resume_id=ResumeId(),
            version_id=ResumeVersionId(),
            raw_text="Extraction pending...",  # Placeholder until OCR runs
            file_path=file_uri,
        )

        # 4. Persist Aggregate
        async with self._uow:
            await self._candidate_repo.save(candidate)
            await self._uow.commit()

        return Result.ok(ResumeMapper.to_output_dto(resume))
