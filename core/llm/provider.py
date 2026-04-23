"""
CoreAgent-2 — LLM Provider Factory
Supports TCS GenAI Lab (via OpenAI-compatible endpoint) and local Ollama models.
The provider / model can be overridden at runtime via session state (Model Router).
"""
import httpx
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

from core.config import config


def get_llm(
    provider: str | None = None,
    model_name: str | None = None,
    temperature: float = 0.2,
    streaming: bool = True,
) -> BaseChatModel:
    """Return an LLM instance for the requested provider."""

    provider = provider or config.DEFAULT_LLM_PROVIDER

    if provider == "TCS_GENAI_LAB":
        model_name = model_name or config.TCS_GENAI_DEFAULT_CHAT_MODEL
        client = httpx.Client(verify=False)
        return ChatOpenAI(
            api_key=config.TCS_GENAI_API_KEY,
            base_url=config.TCS_GENAI_BASE_URL,
            model=model_name,
            temperature=temperature,
            streaming=streaming,
            http_client=client,
        )

    elif provider == "OLLAMA":
        model_name = model_name or config.OLLAMA_DEFAULT_CHAT_MODEL
        return ChatOllama(
            base_url=config.OLLAMA_BASE_URL,
            model=model_name,
            temperature=temperature,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")


def get_reasoning_llm() -> BaseChatModel:
    """Return a model better suited for complex reasoning tasks."""
    if config.DEFAULT_LLM_PROVIDER == "OLLAMA":
        return get_llm(provider="OLLAMA", model_name=config.OLLAMA_DEFAULT_REASONING_MODEL)
    return get_llm()
