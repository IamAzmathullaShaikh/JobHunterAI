import pytest

from domain.discovery.entities import Job
from domain.profile.candidate import Candidate
from domain.profile.entities import Skill
from domain.services.matching.job_matching import JobMatchingService
from domain.shared.enums import SkillCategory
from domain.shared.value_objects import (CandidateId, ContactInfo,
                                         EmailAddress, JobId, Location,
                                         SkillId, SkillLevel)


def test_job_matching_logic():
    # 1. Setup Candidate
    contact = ContactInfo(email=EmailAddress("alex@example.com"))
    candidate = Candidate(id=CandidateId(), _full_name="Alex", _contact_info=contact)
    candidate.add_skill(
        Skill(
            id=SkillId(),
            name="Python",
            category=SkillCategory.TECHNICAL,
            level=SkillLevel(5),
        )
    )

    # 2. Setup Job
    job = Job(
        id=JobId(),
        company_id="comp-1",
        title="Python Dev",
        description="Write python code",
        url="http://jobs.com",
        location=Location(city="NY", country="USA", is_remote=True),
        required_skills=["Python", "SQL"],
    )

    # 3. Calculate Match
    service = JobMatchingService()
    match = service.calculate_match(candidate, job)

    # Should match Python, but miss SQL
    assert "python" in match.matched_skills
    assert "sql" in match.missing_skills
    assert 0.0 < match.overall_score < 1.0
