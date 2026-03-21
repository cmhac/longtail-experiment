"""Quality tooling smoke checks for pipeline baseline artifacts."""

from pathlib import Path


def test_pipeline_quality_configuration_files_exist() -> None:
    """Assert required pipeline quality configuration files exist."""
    assert Path("apps/pipeline/pyproject.toml").exists()
    assert Path("apps/pipeline/uv.lock").exists()
