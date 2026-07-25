import logging

from core.providers.base import ProviderMetadata
from core.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class ProviderLoader:
    """
    Handles discovery and registration of providers into the registry.
    Decouples registration logic from the providers themselves.
    """

    @staticmethod
    def load_all(registry: ProviderRegistry) -> None:
        """Discovers and registers every known provider."""
        logger.info("Starting automated provider discovery...")

        # 1. Register AI Providers
        ProviderLoader._register_ai(registry)

        # 2. Register Scraper Providers
        ProviderLoader._register_scrapers(registry)

        logger.info("Provider discovery complete.")

    @staticmethod
    def _register_ai(registry: ProviderRegistry) -> None:
        # Groq
        from core.providers.ai.groq_provider import GroqAIProvider

        groq_meta = ProviderMetadata(
            provider_id="groq",
            name="Groq Inference Engine",
            version="1.0.0",
            provider_type="ai",
            priority=10,
            capabilities=["json", "streaming", "tool_calling"],
        )
        registry.register(groq_meta, GroqAIProvider)

        # Future AI providers go here

    @staticmethod
    def _register_scrapers(registry: ProviderRegistry) -> None:
        # Apify
        from core.providers.scrapers.apify_provider import ApifyProvider

        apify_meta = ProviderMetadata(
            provider_id="apify",
            name="Apify Cloud Scrapers",
            version="1.0.0",
            provider_type="scraper",
            priority=10,
            capabilities=[
                "keyword_search",
                "location_search",
                "pagination",
                "status_monitoring",
                "cancellation",
                "dataset_export",
            ],
        )
        registry.register(apify_meta, ApifyProvider)

        # Future scraper providers go here
