from application.dto.output.career_assistant_output import (
    CareerAssistantResponseDTO, GenerationMetadataDTO, GenerationResultDTO)


class CareerAssistantMapper:
    """
    Standardizes output mapping for AI-generated content.
    """

    @staticmethod
    def to_unified_response(
        result: GenerationResultDTO, tracking_id: str
    ) -> CareerAssistantResponseDTO:
        return CareerAssistantResponseDTO(result=result, tracking_id=tracking_id)
