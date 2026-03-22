"""Concurrency policy tests for source lock service."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.resources.source_lock_service import SourceLockService


def test_source_lock_allows_one_active_and_one_queued() -> None:
    """One source should accept one active run and one queued trigger."""
    service = SourceLockService()

    assert service.acquire("bls", "run-1") == "acquired"
    assert service.acquire("bls", "run-2") == "queued"
    assert service.acquire("bls", "run-3") == "deduplicated"

    snapshot = service.snapshot("bls")
    assert snapshot.active_run_id == "run-1"
    assert snapshot.queued_trigger_token == "run-2"


def test_releasing_active_promotes_queued_trigger() -> None:
    """Releasing an active run should promote the queued trigger to active."""
    service = SourceLockService()
    service.acquire("bls", "run-1")
    service.acquire("bls", "run-2")

    promoted = service.release("bls", "run-1")

    assert promoted == "run-2"
    snapshot = service.snapshot("bls")
    assert snapshot.active_run_id == "run-2"
    assert snapshot.queued_trigger_token is None
