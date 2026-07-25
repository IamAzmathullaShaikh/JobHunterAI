import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from application.results.result import Failure, FailureType, Result
from domain.shared.exceptions import DomainError
from domain.shared.exceptions import ValidationError as DomainValidationError

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")

logger = logging.getLogger(__name__)


class ApplicationUseCase(ABC, Generic[InputDTO, OutputDTO]):
    """
    Base class for all application use cases.
    Orchestrates logging, validation, and standardized error handling.
    """

    @abstractmethod
    async def _run(self, input_dto: InputDTO) -> Result[OutputDTO]:
        """Subclasses implement the actual business orchestration here."""
        pass

    async def execute(self, input_dto: InputDTO) -> Result[OutputDTO]:
        """
        Template method that executes the use case lifecycle.
        """
        use_case_name = self.__class__.__name__
        start_time = time.perf_counter()

        logger.info(f"Executing Use Case: {use_case_name}")

        try:
            # 1. Application-level validation
            validation_error = self.validate_input(input_dto)
            if validation_error:
                logger.warning(
                    f"Validation failed for {use_case_name}: {validation_error}"
                )
                return Result.validation_fail(validation_error)

            # 2. Execute business orchestration
            result = await self._run(input_dto)

            duration = (time.perf_counter() - start_time) * 1000

            if result.is_success:
                logger.info(
                    f"Use Case {use_case_name} completed successfully in {duration:.2f}ms"
                )
            else:
                logger.error(
                    f"Use Case {use_case_name} failed: {result.failure.message}"
                )

            return result

        except DomainValidationError as e:
            return Result.validation_fail(str(e))
        except DomainError as e:
            return Result.business_fail(str(e))
        except Exception as e:
            logger.exception(f"Unexpected error in {use_case_name}: {e}")
            return Result.fail(
                Failure(
                    type=FailureType.UNEXPECTED,
                    message=f"An internal error occurred: {str(e)}",
                )
            )

    def validate_input(self, input_dto: InputDTO) -> Optional[str]:
        """
        Optional application-level validation.
        Override in subclasses for cross-field or context validation.
        """
        return None
