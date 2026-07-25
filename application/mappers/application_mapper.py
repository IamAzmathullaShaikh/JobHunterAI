from application.dto.output.application_output import ApplicationOutputDTO
from domain.tracking.application import Application


class ApplicationMapper:
    """Maps between Application domain entities and DTOs."""

    @staticmethod
    def to_output_dto(application: Application) -> ApplicationOutputDTO:
        return ApplicationOutputDTO(
            id=str(application.id),
            candidate_id=str(application.candidate_id),
            job_id=str(application.job_id),
            status=application.status.value,
            applied_at=(
                str(application._applied_at) if application._applied_at else None
            ),
        )
