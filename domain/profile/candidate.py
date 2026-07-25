from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from domain.profile.entities import (Certification, Education, Experience,
                                     Resume, ResumeVersion, Skill)
from domain.shared.exceptions import InvariantViolationError, ValidationError
from domain.shared.value_objects import (CandidateId, ContactInfo, ResumeId,
                                         ResumeVersionId, SkillId)


@dataclass
class Candidate:
    id: CandidateId
    _full_name: str
    _contact_info: ContactInfo
    _skills: List[Skill] = field(default_factory=list)
    _experiences: List[Experience] = field(default_factory=list)
    _educations: List[Education] = field(default_factory=list)
    _certifications: List[Certification] = field(default_factory=list)
    _resumes: List[Resume] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def contact_info(self) -> ContactInfo:
        return self._contact_info

    @property
    def skills(self) -> Tuple[Skill, ...]:
        return tuple(self._skills)

    @property
    def experiences(self) -> Tuple[Experience, ...]:
        return tuple(self._experiences)

    @property
    def educations(self) -> Tuple[Education, ...]:
        return tuple(self._educations)

    @property
    def certifications(self) -> Tuple[Certification, ...]:
        return tuple(self._certifications)

    def update_contact(self, contact_info: ContactInfo):
        self._contact_info = contact_info

    def add_skill(self, skill: Skill):
        if any(s.name.lower() == skill.name.lower() for s in self._skills):
            return
        self._skills.append(skill)

    def remove_skill(self, skill_id: SkillId):
        self._skills = [s for s in self._skills if s.id != skill_id]

    def has_skill(self, skill_name: str) -> bool:
        return any(s.name.lower() == skill_name.lower() for s in self._skills)

    def add_experience(self, experience: Experience):
        self._experiences.append(experience)
        self._experiences.sort(key=lambda x: x.start_date, reverse=True)

    def add_resume(
        self,
        resume_id: ResumeId,
        version_id: ResumeVersionId,
        raw_text: str,
        file_path: Optional[str] = None,
    ) -> Resume:
        if not raw_text.strip():
            raise InvariantViolationError("Resume cannot exist without content.")

        initial_version = ResumeVersion(
            id=version_id, version_number=1, raw_text=raw_text, file_path=file_path
        )
        new_resume = Resume(
            id=resume_id, candidate_id=self.id, _current_version=initial_version
        )
        self._resumes.append(new_resume)
        return new_resume

    def latest_resume(self) -> Optional[Resume]:
        return self._resumes[-1] if self._resumes else None

    def add_certification(self, certification: Certification):
        self._certifications.append(certification)

    @property
    def total_years_experience(self) -> float:
        total_days = sum(exp.duration_days for exp in self._experiences)
        return round(total_days / 365.25, 1)
