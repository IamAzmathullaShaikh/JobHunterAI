from abc import abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from core.providers.base import ProviderCostEstimate, ProviderLifecycle


class IAIProvider(ProviderLifecycle):
    """
    Abstract contract for AI (LLM) service providers.
    Every implementation (Groq, Gemini, OpenAI) must satisfy this interface.
    """

    @abstractmethod
    async def generate(
        self, messages: List[Dict[str, str]], config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a standard structured JSON completion.

        Args:
            messages: List of message objects (role, content).
            config: Optional overrides for temperature, max_tokens, etc.

        Returns:
            Dict containing 'data' (parsed JSON) and 'meta' (tokens, latency).
        """
        pass

    @abstractmethod
    async def stream(
        self, messages: List[Dict[str, str]], config: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Provides a real-time token stream for the UI.
        """
        pass

    @abstractmethod
    async def embed(self, text_input: str) -> List[float]:
        """
        Generates a vector embedding for the given input text.
        Replaces local sentence-transformers inference.
        """
        pass

    @abstractmethod
    def estimate_cost(self, messages: List[Dict[str, str]]) -> ProviderCostEstimate:
        """
        Predicts the USD cost for a generation request based on token estimates.
        """
        pass

    @abstractmethod
    def supports(self, feature: str) -> bool:
        """
        Capability detection hook (e.g., 'vision', 'tool_calling', 'structured_output').
        """
        pass
