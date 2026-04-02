"""Compose command regressions for offline-capable local runtime startup."""

from pathlib import Path

BACKEND_BOOTSTRAP_GUARD = (
    "if [ ! -x apps/backend/.venv/bin/alembic ]; then uv sync --project apps/backend --frozen; fi"
)
PIPELINE_BOOTSTRAP_GUARD = (
    "if [ ! -x apps/pipeline/.venv/bin/dagster ]; then uv sync --project apps/pipeline --frozen; fi"
)


def test_backend_service_uses_no_sync_runtime_commands() -> None:
    """Backend compose command should run from pre-synced env without network sync."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert BACKEND_BOOTSTRAP_GUARD in compose
    assert "uv run --project apps/backend --no-sync alembic" in compose
    assert "uv run --project apps/backend --no-sync python -m src.http_api_server" in compose


def test_dagit_service_uses_no_sync_runtime_commands() -> None:
    """Dagit compose command should run from pre-synced env without network sync."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert PIPELINE_BOOTSTRAP_GUARD in compose
    assert "uv run --project apps/pipeline --no-sync dagster dev" in compose
