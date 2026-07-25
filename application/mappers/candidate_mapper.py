from application.dto.output.candidate_output import CandidateOutputDTO
from domain.profile.candidate import Candidate


class CandidateMapper:
    """Maps between Candidate domain entities and DTOs."""

    @staticmethod
    def to_output_dto(candidate: Candidate) -> CandidateOutputDTO:
        return CandidateOutputDTO(
            id=str(candidate.id),
            full_name=candidate.full_name,
            email=candidate.contact_info.email.value,
            phone=(
                candidate.contact_info.phone.value
                if candidate.contact_info.phone
                else None
            ),
            linkedin_url=candidate.contact_info.linkedin_url,
            total_experience=candidate.total_years_experience,
        )
