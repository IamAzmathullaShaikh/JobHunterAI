import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.exceptions import AIProviderError
from core.providers.ai.groq_config import GroqConfig
from core.providers.ai.groq_provider import GroqAIProvider
from core.providers.base import HealthStatus

# --- Tests ---


@pytest.mark.asyncio
async def test_groq_initialization():
    config = GroqConfig(api_key="test-key")
    provider = GroqAIProvider(config)

    # Mock connect to avoid real network call
    with patch(
        "core.providers.ai.groq_client.GroqClient.connect", new_callable=AsyncMock
    ):
        await provider.initialize()
        assert provider._initialized == True
        assert await provider.ready() == True


@pytest.mark.asyncio
async def test_groq_generate_success():
    config = GroqConfig(api_key="test-key")
    provider = GroqAIProvider(config)

    # Mock successful response
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = '{"match": true}'
    mock_resp.usage = MagicMock(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    with patch(
        "core.providers.ai.groq_client.GroqClient.execute_completion",
        new_callable=AsyncMock,
    ) as mock_exec:
        mock_exec.return_value = mock_resp

        result = await provider.generate([{"role": "user", "content": "hi"}])

        assert result["data"]["match"] == True
        assert result["meta"]["total_tokens"] == 15
        assert result["meta"]["provider"] == "official:groq"


@pytest.mark.asyncio
async def test_groq_error_translation():
    config = GroqConfig(api_key="test-key")
    provider = GroqAIProvider(config)

    # Define a mock exception class that matches the name the translator looks for
    class RateLimitError(Exception):
        pass

    with patch(
        "core.providers.ai.groq_client.GroqClient.execute_completion",
        new_callable=AsyncMock,
    ) as mock_exec:
        mock_exec.side_effect = RateLimitError("Quota reached")

        with pytest.raises(AIProviderError) as exc:
            await provider.generate([{"role": "user", "content": "hi"}])

        assert "Quota exceeded" in str(exc.value)


@pytest.mark.asyncio
async def test_groq_streaming():
    config = GroqConfig(api_key="test-key")
    provider = GroqAIProvider(config)

    async def mock_stream_gen(params):
        chunks = ["He", "llo", " world"]
        for c in chunks:
            m = MagicMock()
            m.choices = [MagicMock()]
            m.choices[0].delta.content = c
            yield m

    with patch(
        "core.providers.ai.groq_client.GroqClient.execute_stream",
        side_effect=mock_stream_gen,
    ):
        received = []
        async for chunk in provider.stream([{"role": "user", "content": "hi"}]):
            received.append(chunk)

        assert "".join(received) == "Hello world"


if __name__ == "__main__":

    async def run_all():
        print("Running Groq Provider tests...")
        await test_groq_initialization()
        print("✅ Initialization passed")
        await test_groq_generate_success()
        print("✅ Generation passed")
        await test_groq_error_translation()
        print("✅ Error Translation passed")
        await test_groq_streaming()
        print("✅ Streaming passed")

    asyncio.run(run_all())
