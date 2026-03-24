"""Guardrails that enforce one-file source onboarding bootstrap behavior."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

BOOTSTRAP_SURFACES: tuple[Path, ...] = (
    Path("apps/pipeline/src/orchestration/jobs/source_assets/discovery.py"),
    Path("apps/pipeline/src/orchestration/schedules/source_asset_schedules.py"),
    Path("apps/pipeline/src/orchestration/source_asset_definitions.py"),
    Path("apps/pipeline/src/orchestration/definitions.py"),
    Path("apps/pipeline/src/orchestration/runtime.py"),
)

PROHIBITED_SOURCE_LITERALS: tuple[str, ...] = (
    "fred_fedfunds",
    "fred_gasregw",
    "jobs.sources.fred_fedfunds_source",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_bootstrap_surfaces_exist_and_are_scannable() -> None:
    """Guard should track all bootstrap surfaces that must stay source-agnostic."""
    root = _repo_root()
    for surface in BOOTSTRAP_SURFACES:
        path = root / surface
        assert path.exists(), f"Missing guarded bootstrap surface: {surface}"
        assert path.is_file(), f"Guarded path is not a file: {surface}"


def test_bootstrap_surfaces_do_not_hardcode_source_specific_literals() -> None:
    """No source-specific literals/imports should remain in bootstrap orchestration files."""
    root = _repo_root()

    violations: list[str] = []
    for surface in BOOTSTRAP_SURFACES:
        content = (root / surface).read_text(encoding="utf-8")
        for literal in PROHIBITED_SOURCE_LITERALS:
            if literal in content:
                violations.append(f"{surface}: found prohibited literal '{literal}'")

    assert violations == []


def test_bootstrap_surfaces_have_zero_source_specific_artifacts() -> None:
    """Regression harness: all guarded bootstrap files must remain adapter-agnostic."""
    root = _repo_root()

    for surface in BOOTSTRAP_SURFACES:
        content = (root / surface).read_text(encoding="utf-8")
        assert "jobs.sources." not in content
        assert "FRED_" not in content
