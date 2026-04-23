"""
CoreAgent-2 — Structured Observability Logger
Captures per-node execution metrics and provides session-level aggregation.
"""
import json
import logging
import time
from pathlib import Path

from core.config import DATA_DIR

# ── File-backed logger ───────────────────────────────────────────────────
_log_path = DATA_DIR / "core_agent.log"
logger = logging.getLogger("CoreAgent")
logger.setLevel(logging.INFO)

if not logger.handlers:
    fh = logging.FileHandler(str(_log_path))
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(fh)


# ── In-memory metrics store (shared across a session) ────────────────────
class MetricsStore:
    """Accumulates execution events for the analytics dashboard."""

    def __init__(self):
        self.events: list[dict] = []

    def record(self, thread_id: str, node: str, duration_ms: int, status: str = "SUCCESS", error: str = ""):
        entry = {
            "timestamp": time.strftime("%H:%M:%S"),
            "thread_id": thread_id,
            "node": node,
            "duration_ms": duration_ms,
            "status": status,
            "error": error,
        }
        self.events.append(entry)
        logger.info(json.dumps(entry))

    def get_events(self, limit: int = 100) -> list[dict]:
        return self.events[-limit:]

    def clear(self):
        self.events.clear()


# Global singleton
metrics = MetricsStore()


class ObservabilityTracker:
    """Context-manager that automatically records node execution time."""

    def __init__(self, node_name: str, thread_id: str = "default"):
        self.node_name = node_name
        self.thread_id = thread_id
        self.start = 0.0

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = int((time.time() - self.start) * 1000)
        status = "ERROR" if exc_type else "SUCCESS"
        error = str(exc_val) if exc_val else ""
        metrics.record(self.thread_id, self.node_name, duration, status, error)


def log_execution(node_name: str, thread_id: str = "unknown") -> ObservabilityTracker:
    return ObservabilityTracker(node_name, thread_id)
