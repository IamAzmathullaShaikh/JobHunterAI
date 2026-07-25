class JobHunterAIError(Exception):
    """Base exception for the entire application."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DomainError(JobHunterAIError):
    """Base exception for domain-specific errors."""

    pass


class InvariantViolationError(DomainError):
    """Raised when a business rule/invariant is violated."""

    pass


class BusinessRuleViolationError(DomainError):
    """Raised when a specific business logic rule is broken."""

    pass


class ValidationError(DomainError):
    """Raised when data validation fails within the domain."""

    pass


class JobParsingException(DomainError):
    """Raised when a job description cannot be parsed."""

    pass


class MatchingException(DomainError):
    """Raised when the matching engine encounters an error."""

    pass


class GapAnalysisException(DomainError):
    """Raised when gap analysis fails."""

    pass


class ATSException(DomainError):
    """Raised when ATS scoring encounters an error."""

    pass
