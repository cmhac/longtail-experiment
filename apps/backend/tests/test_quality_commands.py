"""Quality tooling smoke checks for backend baseline artifacts."""

from pathlib import Path


def test_backend_quality_configuration_files_exist() -> None:
    """Assert required backend quality configuration files exist."""
    assert Path("apps/backend/pyproject.toml").exists()
    assert Path("apps/backend/uv.lock").exists()


def test_pipeline_quality_configuration_files_exist() -> None:
    """Assert required pipeline quality configuration files exist."""
    assert Path("apps/pipeline/pyproject.toml").exists()
    assert Path("apps/pipeline/uv.lock").exists()


def test_runtime_discovery_parity_script_exists() -> None:
    """Assert runtime parity verification script is present in local-stack tooling."""
    script_path = Path("tools/quality/local-stack/test-discovery-persisted-parity.sh")
    assert script_path.exists()
    assert script_path.stat().st_mode & 0o111
