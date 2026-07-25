import uuid

import pytest

from domain.shared.exceptions import ValidationError
from domain.shared.value_objects import (CandidateId, EmailAddress, Money,
                                         SalaryRange, SkillLevel)


def test_identifier_wrapping():
    raw_uuid = uuid.uuid4()
    c_id = CandidateId(value=raw_uuid)
    assert str(c_id) == str(raw_uuid)

    c_id_2 = CandidateId.from_str(str(raw_uuid))
    assert c_id == c_id_2


def test_salary_range_invariant():
    m1 = Money(50000, "USD")
    m2 = Money(100000, "USD")
    # Valid
    s = SalaryRange(min_amount=m1, max_amount=m2)
    assert s.min_amount.amount == 50000

    # Invalid amount
    with pytest.raises(ValidationError):
        SalaryRange(min_amount=m2, max_amount=m1)

    # Invalid currency
    m3 = Money(60000, "EUR")
    with pytest.raises(ValidationError):
        SalaryRange(min_amount=m1, max_amount=m3)


def test_email_normalization():
    e = EmailAddress(" ALEX.dev@Example.com ")
    assert e.value == "alex.dev@example.com"
    with pytest.raises(ValidationError):
        EmailAddress("invalid-email")


def test_skill_level_bounds():
    SkillLevel(1)
    SkillLevel(5)
    with pytest.raises(ValidationError):
        SkillLevel(0)
    with pytest.raises(ValidationError):
        SkillLevel(6)
