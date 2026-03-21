"""Workspace registration checks for backend project config."""

from pathlib import Path


def test_backend_project_json_exists() -> None:
    """Assert backend project configuration file is present."""
    assert Path("apps/backend/project.json").exists()


def test_pipeline_project_json_exists() -> None:
    """Assert pipeline project configuration file is present."""
    assert Path("apps/pipeline/project.json").exists()
