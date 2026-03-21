"""Shared DB settings helpers for migration and runtime commands."""

from __future__ import annotations

from collections.abc import Mapping
import os


def _env_value(environment: Mapping[str, str], key: str, default: str) -> str:
    value = environment.get(key)
    if value is None or value == "":
        return default
    return value


def build_local_database_url(*, environment: Mapping[str, str]) -> str:
    """Build a local Postgres URL from LOCAL_DB_* environment variables."""
    user = _env_value(environment, "LOCAL_DB_USER", "longtail")
    password = _env_value(environment, "LOCAL_DB_PASSWORD", "longtail")
    host = _env_value(environment, "LOCAL_DB_HOST", "127.0.0.1")
    port = _env_value(environment, "LOCAL_DB_PORT", "55432")
    name = _env_value(environment, "LOCAL_DB_NAME", "longtail_local")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


def resolve_database_url(
    *,
    explicit_url: str | None,
    environment: Mapping[str, str] | None = None,
) -> str:
    """Resolve DB URL preferring DATABASE_URL, then explicit config, then LOCAL_DB defaults."""
    env = environment or os.environ
    direct_override = env.get("DATABASE_URL")
    if direct_override:
        return direct_override
    if explicit_url:
        return explicit_url
    return build_local_database_url(environment=env)
