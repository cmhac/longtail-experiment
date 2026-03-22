"""Automated checks for feature artifact consistency (Feature 008)."""

from __future__ import annotations

from pathlib import Path

SPEC_PATH = Path("specs/008-add-fred-source/spec.md")
PLAN_PATH = Path("specs/008-add-fred-source/plan.md")
TASKS_PATH = Path("specs/008-add-fred-source/tasks.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_feature_008_artifacts_include_gap_update_protocol_sections() -> None:
    """Spec/plan/tasks should include the required gap-capture protocol sections."""
    spec = _read(SPEC_PATH)
    plan = _read(PLAN_PATH)
    tasks = _read(TASKS_PATH)

    assert "## Gap Log" in spec
    assert "### Gap Log Protocol" in spec
    assert "## Blocker Update Protocol" in plan
    assert "## Gap-Driven Amendment Rules" in tasks


def test_feature_008_gap_log_enforces_required_blocker_fields() -> None:
    """Gap log template should contain mandatory fields for triage and ownership."""
    spec = _read(SPEC_PATH)

    required_headers = [
        "Gap ID",
        "Detected In",
        "Impact",
        "Owner",
        "Resolution Target",
        "Status",
        "Linked Tasks",
    ]

    for header in required_headers:
        assert header in spec
