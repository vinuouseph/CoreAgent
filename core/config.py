"""
CoreAgent-2 — Centralized Configuration
Loads settings from .env and provides typed access via the `config` singleton.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directories exist at import time
for _sub in ("chroma_db", "checkpoints", "uploads"):
    (DATA_DIR / _sub).mkdir(parents=True, exist_ok=True)


class Config:
    """Immutable-ish settings object read from the environment."""

    # ── Provider Routing ─────────────────────────────────────────────────
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "TCS_GENAI_LAB")

    # ── TCS GenAI Lab ────────────────────────────────────────────────────
    TCS_GENAI_API_KEY: str        = os.getenv("TCS_GENAI_API_KEY", "")
    TCS_GENAI_BASE_URL: str       = os.getenv("TCS_GENAI_BASE_URL", "https://genailab.tcs.in")
    TCS_GENAI_DEFAULT_CHAT_MODEL: str = os.getenv(
        "TCS_GENAI_DEFAULT_CHAT_MODEL", "azure_ai/genailab-maas-DeepSeek-V3-0324"
    )
    TCS_GENAI_DEFAULT_EMBEDDING_MODEL: str = os.getenv(
        "TCS_GENAI_DEFAULT_EMBEDDING_MODEL", "azure/genailab-maas-text-embedding-3-large"
    )

    # ── Available TCS Models (for Model Router UI) ───────────────────────
    TCS_AVAILABLE_MODELS: list[str] = [
        "azure/genailab-maas-gpt-35-turbo",
        "azure/genailab-maas-gpt-4o",
        "azure/genailab-maas-gpt-4o-mini",
        "azure_ai/genailab-maas-DeepSeek-R1",
        "azure_ai/genailab-maas-DeepSeek-V3-0324",
        "azure_ai/genailab-maas-Llama-3.2-90B-Vision-Instruct",
        "azure_ai/genailab-maas-Llama-3.3-70B-Instruct",
        "azure_ai/genailab-maas-Llama-4-Maverick-17B-128E-Instruct-FP8",
        "azure_ai/genailab-maas-Phi-3.5-vision-instruct",
        "azure_ai/genailab-maas-Phi-4-reasoning",
    ]

    # ── Local Ollama ─────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str               = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_DEFAULT_CHAT_MODEL: str     = os.getenv("OLLAMA_DEFAULT_CHAT_MODEL", "Llama-3.2-3b-it")
    OLLAMA_DEFAULT_REASONING_MODEL: str = os.getenv("OLLAMA_DEFAULT_REASONING_MODEL", "Deepseek-r1")
    OLLAMA_DEFAULT_EMBEDDING_MODEL: str = os.getenv("OLLAMA_DEFAULT_EMBEDDING_MODEL", "Gte-large")

    OLLAMA_AVAILABLE_MODELS: list[str] = [
        "Llama-3.2-3b-it",
        "Gemma-3-4b-it",
        "Qwen-2.5.1-coder-it",
        "Deepseek-r1",
    ]

    # ── Data Persistence ─────────────────────────────────────────────────
    CHROMA_DB_PATH: str     = os.getenv("CHROMA_DB_PATH", str(DATA_DIR / "chroma_db"))
    CHECKPOINT_DB_PATH: str = os.getenv("CHECKPOINT_DB_PATH", str(DATA_DIR / "checkpoints" / "agent_checkpoints.db"))
    UPLOAD_DIR: str         = os.getenv("UPLOAD_DIR", str(DATA_DIR / "uploads"))

    # ── RAG / Agent Tuning ───────────────────────────────────────────────
    TOP_K_RESULTS: int          = int(os.getenv("TOP_K_RESULTS", "3"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "1.2"))
    MAX_SELF_RAG_RETRIES: int   = int(os.getenv("MAX_SELF_RAG_RETRIES", "3"))


config = Config()
