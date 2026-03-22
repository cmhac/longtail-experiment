"""US2 queued-trigger and deterministic rerun policy tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.resources.source_lock_service import SourceLockService


def test_active_plus_one_queued_trigger_is_enforced() -> None:
    """Policy should enforce one active and one queued trigger per source."""
    service = SourceLockService()

    assert service.acquire("bls", "run-1") == "acquired"
    assert service.acquire("bls", "run-2") == "queued"
    assert service.acquire("bls", "run-3") == "deduplicated"


def test_three_identical_reruns_keep_deterministic_queue_state() -> None:
    """Repeated reruns should deduplicate to the same queued token."""
    service = SourceLockService()

    statuses = [service.acquire("bls", "run-1")]
    statuses.extend(service.acquire("bls", "queued-token") for _ in range(3))

    assert statuses == ["acquired", "queued", "deduplicated", "deduplicated"]
    snapshot = service.snapshot("bls")
    assert snapshot.active_run_id == "run-1"
    assert snapshot.queued_trigger_token == "queued-token"
