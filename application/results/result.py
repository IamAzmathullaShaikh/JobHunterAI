from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class FailureType(str, Enum):
    VALIDATION = "validation_failure"
    BUSINESS = "business_failure"
    INFRASTRUCTURE = "infrastructure_failure"
    REPOSITORY = "repository_failure"
    PROVIDER = "provider_failure"
    NOT_FOUND = "not_found"
    UNEXPECTED = "unexpected_failure"


@dataclass(frozen=True)
class Failure:
    type: FailureType
    message: str
    code: Optional[str] = None
    details: Optional[Any] = None


class Result(Generic[T]):
    """
    Standard result pattern for all Application and Use Case responses.
    Supports functional operations for pipeline composition.
    """

    def __init__(
        self,
        is_success: bool,
        value: Optional[T] = None,
        failure: Optional[Failure] = None,
    ):
        self._is_success = is_success
        self._value = value
        self._failure = failure

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    def unwrap(self) -> T:
        if not self._is_success:
            raise ValueError(
                f"Cannot access value of a failure result: {self._failure.message}"
            )
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value if self._is_success else default

    @property
    def failure(self) -> Failure:
        if self._is_success:
            raise ValueError("Cannot access failure of a success result.")
        return self._failure

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(True, value=value)

    @classmethod
    def fail(cls, failure: Failure) -> "Result[T]":
        return cls(False, failure=failure)

    @classmethod
    def validation_fail(
        cls, message: str, details: Optional[Any] = None
    ) -> "Result[T]":
        return cls.fail(Failure(FailureType.VALIDATION, message, details=details))

    @classmethod
    def business_fail(cls, message: str, code: Optional[str] = None) -> "Result[T]":
        return cls.fail(Failure(FailureType.BUSINESS, message, code=code))

    @classmethod
    def not_found(cls, message: str) -> "Result[T]":
        return cls.fail(Failure(FailureType.NOT_FOUND, message))

    @classmethod
    def infra_fail(cls, message: str) -> "Result[T]":
        return cls.fail(Failure(FailureType.INFRASTRUCTURE, message))

    # --- Functional Operations ---

    def map(self, func: Callable[[T], U]) -> "Result[U]":
        """Transforms the success value if present."""
        if self.is_success:
            return Result.ok(func(self.unwrap()))
        return Result.fail(self.failure)

    def bind(self, func: Callable[[T], "Result[U]"]) -> "Result[U]":
        """Chains another operation that returns a Result."""
        if self.is_success:
            return func(self.unwrap())
        return Result.fail(self.failure)

    def match(
        self, on_success: Callable[[T], U], on_failure: Callable[[Failure], U]
    ) -> U:
        """Executes one of two handlers based on outcome."""
        if self.is_success:
            return on_success(self.unwrap())
        return on_failure(self.failure)
