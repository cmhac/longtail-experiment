"""Contract tests for provider onboarding runbook standardization."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_PATH = REPO_ROOT / "docs/runbooks/provider-onboarding.md"


def test_runbook_requires_bootstrap_as_standard_path() -> None:
    """Runbook should explicitly require bootstrap-first onboarding guidance."""
    text = RUNBOOK_PATH.read_text(encoding="utf-8").lower()

    assert "pnpm run provider:bootstrap" in text
    assert "standard" in text
    assert "first step" in text
