"""Contract tests for HTTP runtime detail safety guards."""

# ruff: noqa: D103

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.http_api_server import _resolve_expected_revision


def test_expected_revision_guard_prefers_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCOVERY_EXPECTED_DB_REVISION", "override_head")
    assert _resolve_expected_revision(environment=os.environ) == "override_head"


def test_expected_revision_guard_raises_when_alembic_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DISCOVERY_EXPECTED_DB_REVISION", raising=False)
    monkeypatch.chdir(Path(__file__).resolve().parents[5])
    # force a path where alembic.ini does not resolve by patching candidates indirectly
    monkeypatch.setattr("src.http_api_server.Path.exists", lambda self: False)

    with pytest.raises(RuntimeError, match="Unable to resolve expected schema revision"):
        _resolve_expected_revision(environment={})
