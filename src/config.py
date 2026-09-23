from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_MANUALS_DIR = DATA_DIR / "raw_manuals"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
SQLITE_DB_PATH = DATA_DIR / "mining_ops.db"

for directory in (DATA_DIR, RAW_MANUALS_DIR, CHROMA_DB_DIR):
    directory.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env", override=False)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")

__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "RAW_MANUALS_DIR",
    "CHROMA_DB_DIR",
    "SQLITE_DB_PATH",
    "OLLAMA_BASE_URL",
    "LLM_MODEL",
    "EMBEDDING_MODEL",
]
