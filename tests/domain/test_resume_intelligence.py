from datetime import date

import pytest

from domain.profile.candidate import Candidate
from domain.profile.entities import Experience, Resume, ResumeVersion, Skill
from domain.services.analysis import (ResumeScoringService,
                                      ResumeSuggestionService)
from domain.shared.enums import SkillCategory
from domain.shared.value_objects import (CandidateId, ContactInfo,
                                         EmailAddress, PhoneNumber, ResumeId,
                                         ResumeVersionId, SkillId, SkillLevel)


@pytest.fixture
def base_candidate():
    contact = ContactInfo(
        email=EmailAddress("test@example.com"),
        phone=PhoneNumber("+1234567890"),
        linkedin_url="https://linkedin.com/in/test",
    )
    return Candidate(id=CandidateId(), _full_name="Tester", _contact_info=contact)


@pytest.fixture
def base_resume(base_candidate):
    v = ResumeVersion(
        id=ResumeVersionId(),
        version_number=1,
        raw_text="Experienced dev with python and java.",
    )
    return Resume(
        id=str(ResumeId()), candidate_id=str(base_candidate.id), _current_version=v
    )


def test_resume_scoring_full(base_resume, base_candidate):
    # Add skills for keyword score
    base_candidate.add_skill(
        Skill(
            id=SkillId(),
            name="Python",
            category=SkillCategory.TECHNICAL,
            level=SkillLevel(5),
        )
    )

    score = ResumeScoringService.calculate_score(base_resume, base_candidate)

    assert score["overall_score"] > 0.5
    assert score["formatting_score"] == 1.0  # Has phone and linkedin


def test_resume_scoring_poor_formatting(base_resume):
    # Candidate with minimal contact info
    poor_candidate = Candidate(
        id=CandidateId(),
        _full_name="No Phone",
        _contact_info=ContactInfo(email=EmailAddress("none@test.com")),
    )

    score = ResumeScoringService.calculate_score(base_resume, poor_candidate)
    assert score["formatting_score"] == 0.5


def test_suggestions_for_missing_experience(base_resume, base_candidate):
    # Candidate with NO experience
    suggestions = ResumeSuggestionService.generate_suggestions(
        base_resume, base_candidate
    )

    messages = [s["message"] for s in suggestions]
    assert any("work experience" in m for m in messages)
    assert any(s["category"] == "experience" for s in suggestions)
