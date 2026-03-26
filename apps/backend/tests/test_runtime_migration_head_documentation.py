"""US3 documentation checks for migration-head runtime expectations."""

from pathlib import Path

EXPECTED_HEAD = "0009_drop_source_profile_frequency"


def test_agents_migration_head_matches_runtime_expectation() -> None:
    """Ensure AGENTS guidance reflects the enforced runtime migration head."""
    agents = Path("AGENTS.md").read_text(encoding="utf-8")

    assert EXPECTED_HEAD in agents


def test_quickstart_mentions_runtime_migration_head_enforcement() -> None:
    """Ensure quickstart documents migration-head runtime enforcement."""
    quickstart = Path("specs/019-real-backend-api/quickstart.md").read_text(encoding="utf-8")

    assert "DISCOVERY_EXPECTED_DB_REVISION" in quickstart
    assert EXPECTED_HEAD in quickstart
