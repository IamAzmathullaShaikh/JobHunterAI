from typing import Any, Dict, Optional

from core.exceptions import ScraperError, ValidationError


def translate_apify_exception(e: Exception, provider_id: str) -> Exception:
    """
    Translates Apify SDK-specific exceptions into standardized internal ones.
    """
    err_type = type(e).__name__
    err_msg = str(e)

    if "ApifyApiError" in err_type:
        # Check status codes if available
        status_code = getattr(e, "status_code", None)
        if status_code == 401:
            return ScraperError(f"Invalid API token: {err_msg}", provider_id)
        if status_code == 429:
            return ScraperError(f"Rate limit exceeded: {err_msg}", provider_id)
        if status_code == 404:
            return ScraperError(
                f"Resource not found (Actor/Dataset): {err_msg}", provider_id
            )

    if "TimeoutError" in err_type:
        return ScraperError(f"Request or Actor timed out: {err_msg}", provider_id)

    if "ValueError" in err_type:
        return ValidationError(f"Invalid input provided to Apify: {err_msg}")

    return ScraperError(f"Unexpected Apify error: {err_msg}", provider_id)
