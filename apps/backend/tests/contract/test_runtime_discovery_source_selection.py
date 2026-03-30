"""Foundational runtime source selection and schema-readiness guards."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.http_api_server import _require_schema_readiness, _resolve_database_url


class _FakeResult:
    def __init__(self, value: str | None) -> None:
        self._value = value

    def scalar_one_or_none(self) -> str | None:
        return self._value


class _FakeConnection:
    def __init__(self, value: str | None) -> None:
        self._value = value

    def execute(self, _statement: object) -> _FakeResult:
        return _FakeResult(self._value)

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        del exc_type, exc, tb


class _FakeEngine:
    def __init__(self, value: str | None) -> None:
        self._value = value

    def connect(self) -> _FakeConnection:
        return _FakeConnection(self._value)


def test_resolve_database_url_prefers_database_url_override() -> None:
    result = _resolve_database_url(
        environment={
            "DATABASE_URL": "postgresql+psycopg://override:secret@db:5432/name",
            "LOCAL_DB_HOST": "localhost",
        }
    )

    assert result == "postgresql+psycopg://override:secret@db:5432/name"


def test_resolve_database_url_uses_local_db_defaults_when_no_override() -> None:
    result = _resolve_database_url(
        environment={
            "LOCAL_DB_USER": "u",
            "LOCAL_DB_PASSWORD": "p",
            "LOCAL_DB_HOST": "h",
            "LOCAL_DB_PORT": "1234",
            "LOCAL_DB_NAME": "n",
        }
    )

    assert result == "postgresql+psycopg://u:p@h:1234/n"


def test_require_schema_readiness_accepts_expected_revision() -> None:
    engine = _FakeEngine("0010_source_profile_metadata")

    _require_schema_readiness(
        engine=engine,
        expected_revision="0010_source_profile_metadata",
    )


def test_require_schema_readiness_rejects_missing_revision() -> None:
    engine = _FakeEngine(None)

    with pytest.raises(RuntimeError, match="schema version is missing"):
        _require_schema_readiness(
            engine=engine,
            expected_revision="0010_source_profile_metadata",
        )


def test_require_schema_readiness_rejects_revision_mismatch() -> None:
    engine = _FakeEngine("0006_previous")

    with pytest.raises(RuntimeError, match="schema revision mismatch"):
        _require_schema_readiness(
            engine=engine,
            expected_revision="0010_source_profile_metadata",
        )
