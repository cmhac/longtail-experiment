"""US3 documentation alignment checks for persisted discovery runtime behavior."""

from pathlib import Path


def test_local_stack_runbook_mentions_persisted_discovery_parity_check() -> None:
    """Ensure local-stack runbook documents persisted parity verification."""
    runbook = Path("docs/runbooks/local-stack-baseline.md").read_text(encoding="utf-8")

    assert "test-discovery-persisted-parity.sh" in runbook
    assert "persisted-data-backed" in runbook


def test_provider_onboarding_mentions_discovery_runtime_surfaces() -> None:
    """Ensure provider onboarding docs name runtime discovery endpoint surfaces."""
    runbook = Path("docs/runbooks/provider-onboarding.md").read_text(encoding="utf-8")

    assert "dataset discovery APIs" in runbook
    assert "home search" in runbook
    assert "catalog" in runbook
    assert "detail" in runbook
