from application.dto.output.resume_output import ResumeOutputDTO
from domain.profile.entities import Resume


class ResumeMapper:
    """Maps between Resume domain entities and DTOs."""

    @staticmethod
    def to_output_dto(resume: Resume) -> ResumeOutputDTO:
        return ResumeOutputDTO(
            id=str(resume.id),
            version=resume.version_count,
            completeness=resume.calculate_completeness(),
            created_at=str(resume.current_version.created_at),
        )
