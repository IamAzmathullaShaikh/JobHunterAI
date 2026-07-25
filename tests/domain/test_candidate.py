from datetime import date

from domain.profile.candidate import Candidate
from domain.profile.entities import Experience
from domain.shared.value_objects import CandidateId, ContactInfo, EmailAddress


def test_candidate_experience_calculation():
    contact = ContactInfo(email=EmailAddress("alex@example.com"))
    c = Candidate(id=CandidateId(), _full_name="Alex Dev", _contact_info=contact)

    # 2 years exp
    e1 = Experience(
        company_name="Tech Co",
        job_title="Dev",
        start_date=date(2020, 1, 1),
        end_date=date(2022, 1, 1),
    )
    c.add_experience(e1)

    assert c.total_years_experience == 2.0


def test_candidate_encapsulation():
    contact = ContactInfo(email=EmailAddress("alex@example.com"))
    c = Candidate(id=CandidateId(), _full_name="Alex Dev", _contact_info=contact)

    # Try to mutate skills list (should be tuple or read-only)
    try:
        c.skills.append("malicious-skill")
    except AttributeError:
        pass  # Expected if property returns tuple

    assert len(c.skills) == 0
