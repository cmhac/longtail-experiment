"""Workspace registration checks for pipeline project config."""

from pathlib import Path


def test_pipeline_project_json_exists() -> None:
    """Assert pipeline project configuration file is present."""
    assert Path("apps/pipeline/project.json").exists()
