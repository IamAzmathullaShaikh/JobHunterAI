from typing import Type

from core.exceptions import (AIProviderError, ProviderInitializationError,
                             ValidationError)


def translate_groq_exception(e: Exception, provider_id: str) -> Exception:
    """
    Translates Groq SDK-specific exceptions into standardized internal ones.
    Ensures zero SDK leakage into the business logic.
    """
    err_type = type(e).__name__
    err_msg = str(e)

    if "AuthenticationError" in err_type or "APIKeyError" in err_type:
        return AIProviderError(f"Invalid API key: {err_msg}", provider_id)

    if "RateLimitError" in err_type:
        return AIProviderError(
            f"Quota exceeded: {err_msg}", provider_id, details={"retry_after": True}
        )

    if "NotFoundError" in err_type:
        return AIProviderError(f"Model not found: {err_msg}", provider_id)

    if "BadRequestError" in err_type:
        return ValidationError(f"Invalid request parameters: {err_msg}")

    if "APITimeoutError" in err_type:
        return AIProviderError(f"Request timed out: {err_msg}", provider_id)

    # Catch-all for other SDK issues
    return AIProviderError(f"Unexpected Groq error: {err_msg}", provider_id)
