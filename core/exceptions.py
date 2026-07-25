from typing import Any, Dict, Optional


class JobHunterException(Exception):
    """Base exception for all JobHunterAI errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AIProviderError(JobHunterException):
    """Raised when an AI provider fails."""

    def __init__(
        self, message: str, provider: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"AI Provider ({provider}) failed: {message}",
            status_code=502,  # Bad Gateway
            details={**(details or {}), "provider": provider},
        )


class ScraperError(JobHunterException):
    """Raised when a job scraper fails."""

    def __init__(
        self, message: str, source: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"Scraper ({source}) failed: {message}",
            status_code=502,
            details={**(details or {}), "source": source},
        )


class DatabaseError(JobHunterException):
    """Raised when a database operation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class ValidationError(JobHunterException):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class ProviderRegistrationError(JobHunterException):
    """Raised when a provider fails the registration validation pipeline."""

    def __init__(
        self, message: str, provider_id: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"Registration failed for '{provider_id}': {message}",
            status_code=500,
            details={**(details or {}), "provider_id": provider_id},
        )


class ProviderInitializationError(JobHunterException):
    """Raised when a provider fails during its initialize() phase."""

    def __init__(
        self, message: str, provider_id: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"Failed to initialize provider '{provider_id}': {message}",
            status_code=500,
            details={**(details or {}), "provider_id": provider_id},
        )


class ProviderNotFoundError(JobHunterException):
    """Raised when requesting a provider that is not in the registry."""

    def __init__(self, provider_id: str):
        super().__init__(
            message=f"Provider '{provider_id}' not found in registry.", status_code=404
        )


class ProviderNotReadyError(JobHunterException):
    """Raised when a provider exists but its ready() check fails."""

    def __init__(self, provider_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Provider '{provider_id}' is not ready for requests.",
            status_code=503,  # Service Unavailable
            details={**(details or {}), "provider_id": provider_id},
        )


class DuplicateInstanceError(JobHunterException):
    """Raised if an internal cache consistency error occurs."""

    def __init__(self, provider_id: str):
        super().__init__(
            message=f"Duplicate instance detected for provider '{provider_id}'.",
            status_code=500,
        )
