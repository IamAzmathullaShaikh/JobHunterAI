from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from domain.shared.enums import ResumeSectionType, SkillCategory
from domain.shared.value_objects import ResumeVersionId, SkillId, SkillLevel


@dataclass
class Skill:
    id: SkillId
    name: str
    category: SkillCategory
    level: SkillLevel
    years_experience: Optional[float] = None


@dataclass
class Experience:
    company_name: str
    job_title: str
    start_date: date
    end_date: Optional[date] = None
    description: str = ""
    is_current: bool = False

    @property
    def duration_days(self) -> int:
        end = self.end_date or date.today()
        return (end - self.start_date).days


@dataclass
class Education:
    institution_name: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = None


@dataclass
class Certification:
    id: str
    name: str
    issuing_organization: str
    issue_date: date
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = None


@dataclass(frozen=True)
class ResumeVersion:
    id: ResumeVersionId
    version_number: int
    raw_text: str
    file_path: Optional[str] = None
    created_at: date = field(default_factory=date.today)


@dataclass
class Resume:
    id: str
    candidate_id: str
    _current_version: ResumeVersion
    _versions: List[ResumeVersion] = field(default_factory=list)

    @property
    def current_version(self) -> ResumeVersion:
        return self._current_version

    @property
    def version_count(self) -> int:
        return len(self._versions) + 1

    def add_version(
        self, id: ResumeVersionId, raw_text: str, file_path: Optional[str] = None
    ):
        new_version_number = self._current_version.version_number + 1
        new_version = ResumeVersion(
            id=id,
            version_number=new_version_number,
            raw_text=raw_text,
            file_path=file_path,
        )
        self._versions.append(self._current_version)
        self._current_version = new_version

    def contains_keyword(self, keyword: str) -> bool:
        return keyword.lower() in self._current_version.raw_text.lower()

    def calculate_completeness(self) -> float:
        """Simple heuristic for resume completeness based on text length and keyword density."""
        if not self._current_version.raw_text:
            return 0.0
        # Placeholder for more complex logic
        score = min(len(self._current_version.raw_text) / 2000, 1.0)
        return round(score, 2)
