"""US1 checks for local DB default profile configuration."""

from pathlib import Path


def test_stack_env_contains_local_db_defaults() -> None:
    """Verify stack env defines canonical LOCAL_DB defaults."""
    env_file = Path("docker/compose/stack.env").read_text(encoding="utf-8")
    assert "LOCAL_DB_HOST=127.0.0.1" in env_file
    assert "LOCAL_DB_PORT=55432" in env_file
    assert "LOCAL_DB_NAME=longtail_local" in env_file
    assert "LOCAL_DB_USER=longtail" in env_file
    assert "LOCAL_DB_PASSWORD=longtail" in env_file
