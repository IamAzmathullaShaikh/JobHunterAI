from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ResumeUploadInputDTO:
    candidate_id: str
    file_content: bytes
    filename: str
    content_type: str


@dataclass(frozen=True)
class AnalyzeResumeInputDTO:
    resume_id: str
