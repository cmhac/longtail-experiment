"""Validation tests for SOURCE_SPEC adapter manifests."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets import discovery
from src.orchestration.jobs.source_assets.discovery import (
    SourceAdapterManifestError,
    SourceBuilderSpec,
    reset_adapter_module_scan_cache_for_tests,
    scan_adapter_modules,
)
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistration
from src.orchestration.jobs.workflow_result import SourceWorkflowResult


class _ObservationRepository:
    def read_latest_observed_on(self, *, series_key: str):
        return None


def _builder(runner: SourceIngestRunner, observation_repository: _ObservationRepository):
    def _handler(request):
        return SourceWorkflowResult(source_key=request.source_key, status="success")

    return SourceWorkflowRegistration(
        workflow_id="wf-test",
        source_key="test-source",
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
    )


def _valid_source_spec(*, source_key: str) -> dict[str, Any]:
    return {
        "source_key": source_key,
        "provider_group_key": source_key,
        "series_item_keys": (f"{source_key}_series",),
        "canonical_series_keys": (f"{source_key}.series",),
        "ownership_mode": "grouped",
        "cron_schedule": "0 * * * *",
        "cadence_label": "hourly",
        "builder": _builder,
    }


def _patch_scan_modules(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module_specs: dict[str, dict[str, Any] | object],
) -> None:
    reset_adapter_module_scan_cache_for_tests()

    fake_package = SimpleNamespace(__path__=["/tmp/fake-sources"])

    def _iter_modules(_path, prefix):
        return [SimpleNamespace(name=f"{prefix}{name}") for name in module_specs]

    def _import_module(name: str):
        if name == discovery.ADAPTER_PACKAGE_NAME:
            return fake_package
        short_name = name.rsplit(".", 1)[-1]
        if short_name not in module_specs:
            raise ImportError(name)
        module_payload = module_specs[short_name]
        if isinstance(module_payload, Exception):
            raise module_payload
        if isinstance(module_payload, dict):
            return SimpleNamespace(SOURCE_SPEC=module_payload)
        return module_payload

    monkeypatch.setattr(discovery.pkgutil, "iter_modules", _iter_modules)
    monkeypatch.setattr(discovery.importlib, "import_module", _import_module)


def test_scan_adapter_modules_returns_sorted_specs_by_source_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Manifest scan should return source specs sorted by source_key."""
    _patch_scan_modules(
        monkeypatch,
        module_specs={
            "z_source": _valid_source_spec(source_key="z-source"),
            "a_source": _valid_source_spec(source_key="a-source"),
        },
    )

    specs = scan_adapter_modules()

    assert [spec.source_key for spec in specs] == ["a-source", "z-source"]


def test_scan_adapter_modules_rejects_missing_source_spec(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Adapter modules without SOURCE_SPEC should fail startup validation."""
    _patch_scan_modules(monkeypatch, module_specs={"broken_source": object()})

    with pytest.raises(SourceAdapterManifestError, match="SOURCE_SPEC must be defined as a dict"):
        scan_adapter_modules()


def test_scan_adapter_modules_rejects_missing_required_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Required manifest fields should produce module-scoped errors."""
    _patch_scan_modules(
        monkeypatch,
        module_specs={
            "broken_source": {
                "source_key": "",
                "provider_group_key": "",
                "series_item_keys": ("series",),
                "canonical_series_keys": ("canonical",),
                "cron_schedule": "",
                "cadence_label": "",
                "builder": _builder,
            }
        },
    )

    with pytest.raises(SourceAdapterManifestError) as exc_info:
        scan_adapter_modules()

    message = str(exc_info.value)
    assert "source_key must be non-empty" in message
    assert "provider_group_key must be non-empty" in message
    assert "cron_schedule must be non-empty" in message
    assert "cadence_label must be one of" in message


def test_scan_adapter_modules_rejects_tuple_length_mismatch_and_empty_series(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Series tuple mismatches and empties should fail manifest validation."""
    _patch_scan_modules(
        monkeypatch,
        module_specs={
            "broken_source": {
                **_valid_source_spec(source_key="broken-source"),
                "series_item_keys": (),
                "canonical_series_keys": ("one", "two"),
            }
        },
    )

    with pytest.raises(SourceAdapterManifestError) as exc_info:
        scan_adapter_modules()

    message = str(exc_info.value)
    assert "series_item_keys must contain at least one key" in message


def test_scan_adapter_modules_rejects_duplicate_source_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Duplicate source_key declarations should identify conflicting modules."""
    _patch_scan_modules(
        monkeypatch,
        module_specs={
            "first_source": _valid_source_spec(source_key="dup-source"),
            "second_source": _valid_source_spec(source_key="dup-source"),
        },
    )

    with pytest.raises(SourceAdapterManifestError) as exc_info:
        scan_adapter_modules()

    message = str(exc_info.value)
    assert "duplicate source_key declared by multiple modules" in message
    assert "first_source" in message
    assert "second_source" in message


def test_scan_adapter_modules_aggregates_multiple_validation_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scan should aggregate import and manifest violations into one startup error."""
    _patch_scan_modules(
        monkeypatch,
        module_specs={
            "missing_spec_source": object(),
            "import_failure_source": ImportError("boom"),
        },
    )

    with pytest.raises(SourceAdapterManifestError) as exc_info:
        scan_adapter_modules()

    message = str(exc_info.value)
    assert "SOURCE_SPEC must be defined as a dict" in message
    assert "module import failed" in message


def test_scan_adapter_modules_rejects_invalid_cron_syntax(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid cron expressions should fail startup with module-scoped diagnostics."""
    _patch_scan_modules(
        monkeypatch,
        module_specs={
            "invalid_cron_source": {
                **_valid_source_spec(source_key="invalid-cron"),
                "cron_schedule": "not a cron",
            }
        },
    )

    with pytest.raises(SourceAdapterManifestError) as exc_info:
        scan_adapter_modules()

    message = str(exc_info.value)
    assert "invalid_cron_source" in message
    assert "cron_schedule is invalid" in message


def test_fred_source_spec_is_discoverable_from_real_adapter_module() -> None:
    """FRED adapter should export a compliant SOURCE_SPEC discovered by scan."""
    reset_adapter_module_scan_cache_for_tests()

    discovered_specs = scan_adapter_modules()
    by_source_key = {spec.source_key: spec for spec in discovered_specs}

    assert "fred_fedfunds" in by_source_key
    spec = by_source_key["fred_fedfunds"]
    assert spec.provider_group_key == "fred"
    assert spec.cadence_label == "daily"
    assert spec.series_item_keys == ("fred_fedfunds", "fred_gasregw")


def test_builder_spec_supports_schedule_metadata_fields() -> None:
    """SourceBuilderSpec should carry cadence and cron metadata for downstream derivation."""
    spec = SourceBuilderSpec(
        source_key="source",
        module_name="tests.source_module",
        builder=_builder,
        cron_schedule="*/15 * * * *",
        cadence_label="hourly",
    )

    assert spec.cron_schedule == "*/15 * * * *"
    assert spec.cadence_label == "hourly"
