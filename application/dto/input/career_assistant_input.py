from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class BaseGenerationInputDTO:
    candidate_id: str
    job_id: Optional[str] = None
    provider_override: Optional[str] = None
    temperature: float = 0.1


@dataclass(frozen=True)
class ResumeTailoringInputDTO(BaseGenerationInputDTO):
    resume_text: str = ""
    target_role: str = ""
    focus_skills: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CoverLetterInputDTO(BaseGenerationInputDTO):
    resume_text: str = ""
    job_description: str = ""
    tone: str = "professional"  # professional, creative, bold


@dataclass(frozen=True)
class OutreachMessageInputDTO(BaseGenerationInputDTO):
    platform: str = "linkedin"  # linkedin, email
    recipient_role: str = "Recruiter"
    company_name: str = ""


@dataclass(frozen=True)
class CareerAdviceInputDTO(BaseGenerationInputDTO):
    topic: str = ""
    current_status: str = ""
