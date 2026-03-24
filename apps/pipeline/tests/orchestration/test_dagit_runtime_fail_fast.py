"""Fail-fast checks for local Dagit startup metadata configuration."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_start_dagit_local_fails_fast_when_metadata_password_missing() -> None:
    """Startup helper should emit metadata-specific diagnostics before launching Dagit."""
    repo_root = Path(__file__).resolve().parents[4]
    completed = subprocess.run(
        ["bash", "tools/quality/local-stack/start-dagit-local.sh"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "DAGSTER_METADATA_DB_HOST": "127.0.0.1",
            "DAGSTER_METADATA_DB_PORT": "55433",
            "DAGSTER_METADATA_DB_NAME": "dagster_local",
            "DAGSTER_METADATA_DB_USER": "dagster",
            "DAGSTER_METADATA_DB_PASSWORD": "",
        },
    )

    assert completed.returncode == 1
    assert "DAGIT_FAILURE_CATEGORY=metadata_config_missing" in completed.stdout


def test_dagit_endpoint_probe_fails_fast_when_metadata_password_missing() -> None:
    """Endpoint probe should fail with metadata diagnostics before HTTP probing."""
    repo_root = Path(__file__).resolve().parents[4]
    completed = subprocess.run(
        ["bash", "tools/quality/local-stack/test-dagit-endpoint.sh"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "DAGSTER_METADATA_DB_HOST": "127.0.0.1",
            "DAGSTER_METADATA_DB_PORT": "55433",
            "DAGSTER_METADATA_DB_NAME": "dagster_local",
            "DAGSTER_METADATA_DB_USER": "dagster",
            "DAGSTER_METADATA_DB_PASSWORD": "",
        },
    )

    assert completed.returncode == 1
    assert "DAGIT_FAILURE_CATEGORY=metadata_config_missing" in completed.stdout
