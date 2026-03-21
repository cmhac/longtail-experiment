"""US3 pipeline regressions for documented local DB setup defects."""

from pathlib import Path


def test_stack_env_keeps_non_conflicting_db_port_default() -> None:
    """Verify local DB port default remains on the non-conflicting value."""
    stack_env = Path("docker/compose/stack.env").read_text(encoding="utf-8")
    assert "LOCAL_DB_PORT=55432" in stack_env


def test_runbook_mentions_explicit_reset_only_policy() -> None:
    """Verify runbook keeps persistent-by-default and explicit reset guidance."""
    runbook = Path("docs/runbooks/local-stack-baseline.md").read_text(encoding="utf-8")
    assert "docker compose down -v" in runbook
    assert "Do not reset the DB during normal development loops." in runbook
