"""Package export smoke tests for orchestration subpackages."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.orchestration.sensors as sensor_packages
import src.sources as source_packages
from src.orchestration.definitions import get_dagit_workspace_module
from src.orchestration.runtime import verify_runtime_wiring_for_dagit


def test_orchestration_subpackage_imports_are_loadable() -> None:
    """Subpackage modules should import successfully for runtime wiring."""
    assert source_packages is not None
    assert sensor_packages is not None


def test_dagit_workspace_module_export_is_stable() -> None:
    """Definitions module should expose a stable Dagit workspace entrypoint path."""
    assert get_dagit_workspace_module() == "src.orchestration.definitions"


def test_runtime_wiring_validation_helper_is_importable() -> None:
    """Runtime module should export Dagit wiring validation helper."""
    assert callable(verify_runtime_wiring_for_dagit)


def test_compose_is_canonical_dagit_entrypoint() -> None:
    """Onboarding docs should direct Dagit startup through docker compose."""
    runbook = Path("docs/runbooks/provider-onboarding.md").read_text(encoding="utf-8")

    assert "docker compose up -d dagit" in runbook
    assert "docker compose ps dagit" in runbook
