import logging

from core.providers.base import ProviderMetadata
from core.providers.registry import registry
from core.providers.scrapers.apify_provider import ApifyProvider

logger = logging.getLogger(__name__)

# Registration is now handled by core.provider_loader.ProviderLoader during application startup.
