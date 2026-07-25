import logging

from core.providers.ai.groq_models import GROQ_MODEL_CATALOG
from core.providers.ai.groq_provider import GroqAIProvider
from core.providers.base import ProviderMetadata
from core.providers.registry import registry

logger = logging.getLogger(__name__)

# Registration is now handled by core.provider_loader.ProviderLoader during application startup.
