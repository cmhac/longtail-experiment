"""Source-level run lock service enforcing one-active-one-queued policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class SourceLockSnapshot:
    """Immutable lock state snapshot for one source."""

    source_key: str
    active_run_id: str | None
    queued_trigger_token: str | None
    lock_updated_at: datetime


class SourceLockService:
    """Manage source run concurrency with active+queued dedup semantics."""

    def __init__(self) -> None:
        """Initialize empty in-memory lock state."""
        self._state: dict[str, SourceLockSnapshot] = {}

    def acquire(self, source_key: str, trigger_token: str) -> str:
        """Acquire active slot or enqueue one deduplicated pending trigger."""
        now = datetime.now(tz=UTC)
        current = self._state.get(source_key)
        if current is None or current.active_run_id is None:
            self._state[source_key] = SourceLockSnapshot(
                source_key=source_key,
                active_run_id=trigger_token,
                queued_trigger_token=None,
                lock_updated_at=now,
            )
            return "acquired"

        if current.queued_trigger_token is None:
            self._state[source_key] = SourceLockSnapshot(
                source_key=source_key,
                active_run_id=current.active_run_id,
                queued_trigger_token=trigger_token,
                lock_updated_at=now,
            )
            return "queued"

        return "deduplicated"

    def release(self, source_key: str, active_run_id: str) -> str | None:
        """Release active run and promote queued trigger when available."""
        current = self._state.get(source_key)
        if current is None or current.active_run_id != active_run_id:
            return None

        now = datetime.now(tz=UTC)
        if current.queued_trigger_token is None:
            self._state[source_key] = SourceLockSnapshot(
                source_key=source_key,
                active_run_id=None,
                queued_trigger_token=None,
                lock_updated_at=now,
            )
            return None

        promoted = current.queued_trigger_token
        self._state[source_key] = SourceLockSnapshot(
            source_key=source_key,
            active_run_id=promoted,
            queued_trigger_token=None,
            lock_updated_at=now,
        )
        return promoted

    def snapshot(self, source_key: str) -> SourceLockSnapshot:
        """Return current lock state for one source."""
        if source_key in self._state:
            return self._state[source_key]
        return SourceLockSnapshot(
            source_key=source_key,
            active_run_id=None,
            queued_trigger_token=None,
            lock_updated_at=datetime.now(tz=UTC),
        )
