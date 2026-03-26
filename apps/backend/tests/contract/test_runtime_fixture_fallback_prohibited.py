"""US2 integration checks for runtime fixture fallback prohibition."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.http_api_server import _require_schema_readiness


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


def test_pre_migration_runtime_startup_is_blocked_by_schema_guard() -> None:
    with pytest.raises(RuntimeError, match="schema revision mismatch"):
        _require_schema_readiness(
            engine=_FakeEngine("0007_dataset_metadata_topic_tags"),
            expected_revision="0009_drop_source_profile_frequency",
        )


def test_runtime_module_has_no_seed_fallback_import_paths() -> None:
    server_source = Path("apps/backend/src/http_api_server.py").read_text(encoding="utf-8")

    assert "load_discovery_seed_data" not in server_source
    assert "RuntimeDatasetDiscoveryRepository" not in server_source
