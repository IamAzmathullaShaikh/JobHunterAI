import pytest

from application.mappers.candidate_mapper import CandidateMapper
from domain.profile.candidate import Candidate
from domain.shared.value_objects import CandidateId, ContactInfo, EmailAddress


def test_candidate_mapper():
    c_id = CandidateId()
    contact = ContactInfo(email=EmailAddress("test@test.com"))
    candidate = Candidate(id=c_id, _full_name="Tester", _contact_info=contact)

    dto = CandidateMapper.to_output_dto(candidate)

    assert dto.id == str(c_id)
    assert dto.full_name == "Tester"
    assert dto.email == "test@test.com"
