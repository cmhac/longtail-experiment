"""Package export smoke tests for orchestration subpackages."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.orchestration.jobs.sources as source_packages
import src.orchestration.sensors as sensor_packages
from src.orchestration.definitions import get_dagit_workspace_module
from src.orchestration.runtime import verify_runtime_wiring_for_dagit


def test_orchestration_subpackage_imports_are_loadable() -> None:
    """Subpackage modules should import successfully for runtime wiring."""
    assert source_packages is not None
    assert sensor_packages is not None


def test_dagit_workspace_module_export_is_stable() -> None:
    """Definitions module should expose a stable Dagit workspace entrypoint path."""
    assert get_dagit_workspace_module() == "src.orchestration.definitions"


def test_runtime_wiring_validation_helper_is_importable() -> None:
    """Runtime module should export Dagit wiring validation helper."""
    assert callable(verify_runtime_wiring_for_dagit)


def test_dagit_start_helper_fails_from_non_repo_working_directory() -> None:
    """Startup helper should fail with prerequisite category when run outside repo root."""
    repo_root = Path(__file__).resolve().parents[4]

    with tempfile.TemporaryDirectory() as temp_dir:
        completed = subprocess.run(
            ["bash", str(repo_root / "tools/quality/local-stack/start-dagit-local.sh")],
            cwd=temp_dir,
            check=False,
            capture_output=True,
            text=True,
        )

    assert completed.returncode == 1
    assert "DAGIT_FAILURE_CATEGORY=prerequisite_missing" in completed.stdout


def test_dagit_endpoint_probe_fails_for_empty_workspace_graphql_response() -> None:
    """Endpoint helper should fail when GraphQL workspace response has no location entries."""

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/graphql":
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                b'{"data":{"workspaceOrError":{"__typename":"Workspace","locationEntries":[]}}}'
            )

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            return

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    repo_root = Path(__file__).resolve().parents[4]
    try:
        completed = subprocess.run(
            ["bash", "tools/quality/local-stack/test-dagit-endpoint.sh"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "DAGIT_ENDPOINT": f"http://127.0.0.1:{server.server_port}",
                "DAGIT_VERIFY_WORKSPACE": "1",
                "DAGSTER_METADATA_DB_HOST": "127.0.0.1",
                "DAGSTER_METADATA_DB_PORT": "55433",
                "DAGSTER_METADATA_DB_NAME": "dagster_local",
                "DAGSTER_METADATA_DB_USER": "dagster",
                "DAGSTER_METADATA_DB_PASSWORD": "test",
            },
        )
    finally:
        server.shutdown()
        server.server_close()

    assert completed.returncode == 1
    assert "DAGIT_FAILURE_CATEGORY=workspace_load_failed" in completed.stdout
