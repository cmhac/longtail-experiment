"""Contract tests for onboard-provider skill bootstrap requirements."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_PATH = REPO_ROOT / ".agents/skills/onboard-provider/SKILL.md"


def test_skill_requires_runbook_read_and_bootstrap_command() -> None:
    """Skill instructions should mandate runbook read and bootstrap command usage."""
    text = SKILL_PATH.read_text(encoding="utf-8").lower()

    assert "docs/runbooks/provider-onboarding.md" in text
    assert "pnpm run provider:bootstrap" in text
    assert "before" in text and "create" in text
