from typing import Dict, List, Set

from pydantic import BaseModel


class ModelMetadata(BaseModel):
    """Metadata about an LLM model available on Groq."""

    id: str
    name: str
    context_window: int
    capabilities: Set[str]
    is_reasoning: bool = False


# Canonical catalog of Groq models supported by JobHunterAI
GROQ_MODEL_CATALOG: Dict[str, ModelMetadata] = {
    "llama-3.3-70b-versatile": ModelMetadata(
        id="llama-3.3-70b-versatile",
        name="Llama 3.3 70B Versatile",
        context_window=128000,
        capabilities={"json", "tool_calling", "streaming"},
    ),
    "llama-3.1-8b-instant": ModelMetadata(
        id="llama-3.1-8b-instant",
        name="Llama 3.1 8B Instant",
        context_window=131072,
        capabilities={"json", "tool_calling", "streaming"},
    ),
    "mixtral-8x7b-32768": ModelMetadata(
        id="mixtral-8x7b-32768",
        name="Mixtral 8x7B Instruct",
        context_window=32768,
        capabilities={"json", "streaming"},
    ),
    "deepseek-r1-distill-llama-70b": ModelMetadata(
        id="deepseek-r1-distill-llama-70b",
        name="DeepSeek R1 Distill Llama 70B",
        context_window=128000,
        capabilities={"json", "streaming"},
        is_reasoning=True,
    ),
}


def get_model_metadata(model_id: str) -> ModelMetadata:
    """Retrieves metadata for a specific model ID."""
    return GROQ_MODEL_CATALOG.get(
        model_id,
        ModelMetadata(
            id=model_id, name=model_id, context_window=4096, capabilities={"streaming"}
        ),
    )
