import asyncio

import pytest

from application.results.result import Result
from application.use_cases.base import ApplicationUseCase
from domain.shared.exceptions import ValidationError as DomainValidationError


class MockUseCase(ApplicationUseCase[str, str]):
    async def _run(self, input_dto: str) -> Result[str]:
        if input_dto == "fail":
            raise RuntimeError("Unexpected")
        if input_dto == "domain":
            raise DomainValidationError("Invalid Invariant")
        return Result.ok(f"Hello {input_dto}")

    def validate_input(self, input_dto: str):
        if input_dto == "invalid":
            return "Too short"
        return None


def async_test(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@async_test
async def test_use_case_success():
    uc = MockUseCase()
    res = await uc.execute("World")
    assert res.is_success
    assert res.unwrap() == "Hello World"


@async_test
async def test_use_case_validation_fail():
    uc = MockUseCase()
    res = await uc.execute("invalid")
    assert res.is_failure
    assert res.failure.type == "validation_failure"


@async_test
async def test_use_case_domain_fail():
    uc = MockUseCase()
    res = await uc.execute("domain")
    assert res.is_failure
    assert res.failure.message == "Invalid Invariant"


@async_test
async def test_use_case_unexpected_fail():
    uc = MockUseCase()
    res = await uc.execute("fail")
    assert res.is_failure
    assert "internal error" in res.failure.message
