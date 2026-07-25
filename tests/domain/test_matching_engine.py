from datetime import datetime

import pytest

from domain.discovery.entities import Job, JobRequirement
from domain.profile.candidate import Candidate
from domain.profile.entities import Experience, Resume, ResumeVersion, Skill
from domain.services.matching.ats_scoring import ATSScoringService
from domain.services.matching.experience_matching import \
    ExperienceMatchingService
from domain.services.matching.job_matching import JobMatchingService
from domain.services.matching.skill_matching import SkillMatchingService
from domain.shared.enums import ExperienceLevel, SkillCategory
from domain.shared.value_objects import (CandidateId, ContactInfo,
                                         EmailAddress, JobId, Location, Money,
                                         ResumeId, ResumeVersionId,
                                         SalaryRange, SkillId, SkillLevel)


@pytest.fixture
def sample_candidate():
    contact = ContactInfo(email=EmailAddress("dev@example.com"))
    candidate = Candidate(id=CandidateId(), _full_name="Alex", _contact_info=contact)
    candidate.add_skill(
        Skill(
            id=SkillId(),
            name="Python",
            category=SkillCategory.TECHNICAL,
            level=SkillLevel(5),
        )
    )
    candidate.add_skill(
        Skill(
            id=SkillId(),
            name="Docker",
            category=SkillCategory.TECHNICAL,
            level=SkillLevel(4),
        )
    )

    from datetime import date

    candidate.add_experience(
        Experience(
            company_name="Old Co",
            job_title="Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 1, 1),
            description="Worked with Python and Docker",
        )
    )

    # Add a resume
    candidate.add_resume(
        resume_id=ResumeId(),
        version_id=ResumeVersionId(),
        raw_text="Experienced Python Developer. Knowledge of Docker and AWS.",
    )
    return candidate


@pytest.fixture
def sample_job():
    return Job(
        id=JobId(),
        company_id="comp-1",
        title="Senior Python Engineer",
        description="Looking for Python and Kubernetes expert.",
        url="http://jobs.com/1",
        location=Location(city="Berlin", country="Germany", is_remote=False),
        required_skills=["Python", "Kubernetes"],
        preferred_skills=["Docker"],
        experience_level=ExperienceLevel.SENIOR,
    )


def test_skill_matching(sample_candidate, sample_job):
    score, matched, missing = SkillMatchingService.calculate_score(
        sample_candidate, sample_job
    )

    assert "python" in matched
    assert "kubernetes" in missing
    assert "docker" in matched  # Preferred
    assert score > 0.4  # (1/2 * 0.8) + (1/1 * 0.2) = 0.4 + 0.2 = 0.6


def test_experience_matching(sample_candidate, sample_job):
    # Candidate has 3 years. Senior job (5 years)
    score = ExperienceMatchingService.calculate_score(sample_candidate, sample_job)
    assert score == 0.6  # 3/5


def test_full_job_matching(sample_candidate, sample_job):
    result = JobMatchingService.calculate_match(sample_candidate, sample_job)

    assert result.overall_score > 0.0
    assert result.breakdown.skills_score > 0.0
    assert result.breakdown.experience_score > 0.0
    assert len(result.matched_skills) >= 1


def test_ats_scoring(sample_candidate):
    resume = sample_candidate.latest_resume()
    score = ATSScoringService.analyze(resume, sample_candidate)

    assert score.overall_score > 0.0
    assert "contact" in score.section_scores
    # Should have recommendation for missing phone
    assert any(r.category == "contact" for r in score.recommendations)
