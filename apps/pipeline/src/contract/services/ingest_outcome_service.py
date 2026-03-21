"""Outcome helpers for accepted and quarantined ingest records."""

from __future__ import annotations

from src.contract.errors import ContractQuarantineError


def accepted_outcome(series_key: str) -> dict[str, str]:
    """Build an accepted outcome payload."""
    return {"status": "accepted", "series_key": series_key}


def quarantined_outcome(reason: str) -> dict[str, str]:
    """Build a quarantined outcome payload and enforce non-empty reason."""
    if not reason.strip():
        raise ContractQuarantineError("quarantine reason is required")
    return {"status": "quarantined", "reason": reason}
