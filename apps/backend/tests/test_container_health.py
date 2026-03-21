"""Compose health declaration checks for backend placeholder service."""

from pathlib import Path


def test_compose_contains_backend_service() -> None:
    """Assert compose file includes backend service and healthcheck stanza."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "backend:" in compose
    assert "pipeline:" in compose
    assert "healthcheck:" in compose
