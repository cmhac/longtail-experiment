"""Repository interface contracts for shared DB interactions."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class ObservationRepository(Protocol):
    """Contract for persisting and reading canonical observations."""

    def upsert_value(self, series_key: str, observed_on: date, value: Decimal) -> None:
        """Insert or replace an observation value."""
        ...


@runtime_checkable
class ProvenanceRepository(Protocol):
    """Contract for storing immutable provenance records."""

    def add_release(
        self, observation_id: str, release_id: str, source_url: str
    ) -> None:
        """Attach release metadata to an observation."""
        ...


@runtime_checkable
class HierarchyRepository(Protocol):
    """Contract for hierarchy descendant lookups used by backend filters."""

    def get_descendant_ids(self, node_id: str) -> list[str]:
        """Return descendant node ids for category or geography filters."""
        ...


@runtime_checkable
class DatasetDiscoveryReadRepository(Protocol):
    """Contract for search, catalog, recent, and detail read workflows."""

    def search_datasets(
        self,
        *,
        query_text: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated dataset search items and total item count."""
        ...

    def list_recent_datasets(self, *, limit: int) -> list[dict[str, object]]:
        """Return recent dataset summaries ordered by recency descending."""
        ...

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        source_id: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated catalog items with optional filters and total count."""
        ...

    def get_dataset_detail(self, *, dataset_id: str) -> dict[str, object] | None:
        """Return metadata for one dataset by canonical identifier."""
        ...

    def list_dataset_observations(
        self,
        *,
        dataset_id: str,
        from_date: date | None,
        to_date: date | None,
    ) -> list[dict[str, object]]:
        """Return one dataset's observations in ascending observed date order."""
        ...


@runtime_checkable
class TrendLifecycleRepository(Protocol):
    """Contract for trend lifecycle persistence and summary reads."""

    def upsert_trend_record(self, payload: dict[str, object]) -> str:
        """Insert one trend lifecycle record and return canonical id."""
        ...

    def append_transition(self, payload: dict[str, object]) -> None:
        """Persist one immutable trend lifecycle transition event."""
        ...

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        """Return persisted trend record count for one series."""
        ...

    def count_canonical_descriptors_for_series(self, *, series_key: str) -> int:
        """Return persisted canonical descriptor count for one series."""
        ...

    def upsert_lookback_applicability(self, payload: dict[str, object]) -> None:
        """Persist one applicability decision for series/observation/lookback."""
        ...

    def upsert_lookback_snapshot(self, payload: dict[str, object]) -> None:
        """Persist one lookback trend snapshot for series/observation/lookback."""
        ...

    def upsert_canonical_descriptor(self, payload: dict[str, object]) -> None:
        """Persist one canonical descriptor snapshot for series/observation."""
        ...

    def get_previous_canonical_direction(
        self,
        *,
        series_key: str,
        observed_on: date,
    ) -> str | None:
        """Return latest canonical direction before observed date when present."""
        ...

    def append_trend_change_event(
        self, payload: dict[str, object]
    ) -> dict[str, object]:
        """Persist one idempotent trend-change event row and metadata."""
        ...

    def fan_out_notifications_for_event(self, *, event_id: str) -> int:
        """Fan out one user-visible trend event to active subscriptions."""
        ...


@runtime_checkable
class AuthManagementRepository(Protocol):
    """Contract for auth/account persistence and session lifecycle operations."""

    def create_user_account(
        self,
        *,
        email: str,
        password_hash: str,
        display_name: str | None,
        is_admin: bool,
    ) -> dict[str, object]:
        """Create one account and active credential record."""
        ...

    def get_user_by_email(self, *, email: str) -> dict[str, object] | None:
        """Return one account snapshot by normalized email when present."""
        ...

    def get_user_by_id(self, *, user_id: str) -> dict[str, object] | None:
        """Return one account snapshot by canonical user id when present."""
        ...

    def update_failed_sign_in(
        self,
        *,
        user_id: str,
        failed_sign_in_count: int,
        lockout_until: str | None,
    ) -> None:
        """Persist updated failed-sign-in and lockout metadata."""
        ...

    def update_password_hash(self, *, user_id: str, password_hash: str) -> None:
        """Rotate active credential hash for one account."""
        ...

    def update_user_profile(
        self,
        *,
        user_id: str,
        email: str | None,
        display_name: str | None,
    ) -> dict[str, object] | None:
        """Update one account profile projection and return latest snapshot."""
        ...

    def create_session(
        self,
        *,
        user_id: str,
        expires_at: str,
        client_metadata: dict[str, object] | None,
    ) -> dict[str, object]:
        """Create one active session row and return serialized metadata."""
        ...

    def get_active_session(self, *, session_id: str) -> dict[str, object] | None:
        """Return one active session snapshot when present and not expired."""
        ...

    def list_active_sessions(self, *, user_id: str) -> list[dict[str, object]]:
        """Return active sessions for one account ordered by recency."""
        ...

    def revoke_session(self, *, user_id: str, session_id: str, reason: str) -> bool:
        """Revoke one session for one user and return whether a row changed."""
        ...

    def revoke_all_sessions_for_user(self, *, user_id: str, reason: str) -> int:
        """Revoke all active sessions for one user and return affected row count."""
        ...

    def list_admin_users(self) -> list[dict[str, object]]:
        """Return account snapshots for admin management flows."""
        ...

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: str,
    ) -> tuple[dict[str, object] | None, int]:
        """Update account status and return updated account plus revoked sessions."""
        ...

    def update_admin_user_role(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        role_action: str,
    ) -> dict[str, object] | None:
        """Apply admin role update action and return updated account projection."""
        ...

    def revoke_all_sessions_for_user_as_admin(
        self, *, user_id: str, reason: str
    ) -> int:
        """Revoke all sessions for target user from admin workflows."""
        ...

    def write_audit_event(
        self,
        *,
        event_type: str,
        user_id: str | None,
        actor_user_id: str | None,
        event_context: dict[str, object] | None,
    ) -> None:
        """Append one immutable audit row for auth/account actions."""
        ...


@runtime_checkable
class TrendNotificationRepository(Protocol):
    """Contract for trend-change notification persistence operations."""

    def get_previous_canonical_direction(
        self,
        *,
        series_key: str,
        observed_on: date,
    ) -> str | None:
        """Return latest prior canonical direction before observed date."""
        ...

    def append_trend_change_event(
        self, payload: dict[str, object]
    ) -> dict[str, object]:
        """Persist one reversal event idempotently and return event metadata."""
        ...

    def fan_out_notifications_for_event(self, *, event_id: str) -> int:
        """Fan out one user-visible event to active subscriptions."""
        ...

    def list_notifications(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None,
        unread_only: bool,
    ) -> dict[str, object]:
        """Return one paginated newest-first notification listing payload."""
        ...

    def get_unread_summary(self, *, user_id: str) -> dict[str, object]:
        """Return unread count and latest-delivery summary for one user."""
        ...

    def mark_notification_read(self, *, user_id: str, notification_id: str) -> bool:
        """Mark one notification read for one user."""
        ...

    def mark_notification_unread(self, *, user_id: str, notification_id: str) -> bool:
        """Mark one notification unread for one user."""
        ...

    def mark_all_notifications_read(self, *, user_id: str) -> int:
        """Mark all unread notifications read for one user."""
        ...

    def list_active_subscriptions(self, *, user_id: str) -> list[dict[str, object]]:
        """Return active dataset subscriptions for one user."""
        ...

    def create_or_reactivate_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
        now: datetime,
    ) -> dict[str, object] | None:
        """Create or reactivate one dataset subscription for one user."""
        ...

    def remove_active_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
        now: datetime,
    ) -> bool:
        """Deactivate one dataset subscription when currently active."""
        ...

    def enforce_notification_retention_policy(
        self,
        *,
        now: datetime,
        retention_days: int = 365,
    ) -> int:
        """Remove retention-eligible read notifications and return deleted count."""
        ...
