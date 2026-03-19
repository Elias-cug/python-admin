from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    # Load project root `.env` once; do not override already-exported env vars.
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    database_url: str
    db_schema: str | None = None


def _build_database_url() -> str:
    if url := os.getenv("DATABASE_URL"):
        return url

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")

    missing = [
        k
        for k, v in [
            ("DB_HOST", host),
            ("DB_USER", user),
            ("DB_PASSWORD", password),
            ("DB_NAME", name),
        ]
        if not v
    ]
    if missing:
        raise RuntimeError(
            "Database config missing in .env: set DATABASE_URL or " + ", ".join(missing)
        )

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_env()
    return Settings(
        database_url=_build_database_url(),
        db_schema=os.getenv("DB_SCHEMA") or None,
    )
