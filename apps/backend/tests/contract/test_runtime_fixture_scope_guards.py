"""Foundational guards for fixture usage scope in runtime discovery paths."""

# ruff: noqa: D103

from __future__ import annotations

from pathlib import Path


def test_http_server_runtime_wiring_does_not_import_seed_loader() -> None:
    server_source = Path("apps/backend/src/http_api_server.py").read_text(encoding="utf-8")

    assert "load_discovery_seed_data" not in server_source
    assert "RuntimeDatasetDiscoveryRepository" not in server_source


def test_fixture_module_remains_available_for_test_scope() -> None:
    fixture_source = Path("apps/backend/tests/fixtures/dataset_discovery_fixture.py").read_text(
        encoding="utf-8"
    )

    assert "_DISCOVERY_FIXTURE" in fixture_source
    assert "dataset_discovery_fixture" in fixture_source
