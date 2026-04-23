"""
CoreAgent-2 — SQLite Checkpointer
Provides enterprise-grade state persistence for LangGraph via SQLite.
"""
import os
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from core.config import config


def get_checkpointer() -> SqliteSaver:
    """
    Create and return a SQLite-backed checkpointer.
    The database file is created at config.CHECKPOINT_DB_PATH.
    """
    db_path = config.CHECKPOINT_DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    return SqliteSaver(conn)
