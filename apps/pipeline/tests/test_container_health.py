"""Compose health declaration checks for pipeline placeholder service."""

from pathlib import Path


def test_compose_contains_pipeline_service() -> None:
    """Assert compose file includes pipeline service and healthcheck stanza."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "pipeline:" in compose
    assert "healthcheck:" in compose
