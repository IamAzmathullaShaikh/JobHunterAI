import pytest

from application.results.result import Failure, FailureType, Result


def test_result_success():
    res = Result.ok("data")
    assert res.is_success
    assert res.unwrap() == "data"


def test_result_failure():
    fail = Failure(FailureType.VALIDATION, "error")
    res = Result.fail(fail)
    assert res.is_failure
    assert res.failure.message == "error"
    with pytest.raises(ValueError):
        res.unwrap()


def test_result_map():
    res = Result.ok(10).map(lambda x: x * 2)
    assert res.unwrap() == 20

    fail_res = Result.validation_fail("err").map(lambda x: x * 2)
    assert fail_res.is_failure


def test_result_bind():
    res = Result.ok(10).bind(lambda x: Result.ok(x + 5))
    assert res.unwrap() == 15

    fail_res = Result.ok(10).bind(lambda x: Result.business_fail("err"))
    assert fail_res.is_failure


def test_result_match():
    res = Result.ok("win")
    val = res.match(
        on_success=lambda x: f"Yay {x}", on_failure=lambda f: f"No {f.message}"
    )
    assert val == "Yay win"
