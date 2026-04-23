"""
CoreAgent-2 — Embedding Model Factory
Returns the right Embeddings implementation based on the active provider.
"""
import httpx
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.embeddings import Embeddings

from core.config import config


def get_embeddings(provider: str | None = None, model_name: str | None = None) -> Embeddings:
    """Factory for embedding models."""

    provider = provider or config.DEFAULT_LLM_PROVIDER

    if provider == "TCS_GENAI_LAB":
        model_name = model_name or config.TCS_GENAI_DEFAULT_EMBEDDING_MODEL
        client = httpx.Client(verify=False)
        return OpenAIEmbeddings(
            api_key=config.TCS_GENAI_API_KEY,
            base_url=config.TCS_GENAI_BASE_URL,
            model=model_name,
            http_client=client,
        )

    elif provider == "OLLAMA":
        model_name = model_name or config.OLLAMA_DEFAULT_EMBEDDING_MODEL
        return OllamaEmbeddings(
            base_url=config.OLLAMA_BASE_URL,
            model=model_name,
        )

    raise ValueError(f"Unsupported embedding provider: {provider}")
