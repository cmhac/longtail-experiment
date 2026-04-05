# Data Model: In-App Trend Change Notifications

## Entity: TrendChangeEvent

- Purpose: Immutable canonical record for one detected `up <-> down` reversal.
- Fields:
  - event_id (UUID, required)
  - data_series_id (string, required)
  - canonical_series_key (string, required)
  - previous_direction (enum: `up` | `down`, required)
  - current_direction (enum: `up` | `down`, required)
  - effective_observed_on (date, required)
  - processing_context (enum: `incremental` | `historical_reprocessing`, required)
  - visibility_classification (enum: `user_visible` | `audit_only`, required)
  - emitted_at (timestamp with time zone, required)
  - idempotency_fingerprint (string, required)
- Validation rules:
  - Events are created only when both directions are non-null and differ.
  - `processing_context=historical_reprocessing` defaults to `visibility_classification=audit_only`.
  - `idempotency_fingerprint` is globally unique.

## Entity: UserDatasetSubscription

- Purpose: User-owned eligibility mapping for notification fan-out.
- Fields:
  - subscription_id (UUID, required)
  - user_id (UUID, required)
  - data_series_id (string, required)
  - subscribed_at (timestamp with time zone, required)
  - unsubscribed_at (timestamp with time zone | null)
  - updated_at (timestamp with time zone, required)
- Validation rules:
  - Active subscription is represented by `unsubscribed_at = null`.
  - A user has at most one active subscription per dataset.
  - New users default to zero subscriptions.

## Entity: UserTrendNotification

- Purpose: Per-user in-app notification instance derived from one user-visible event.
- Fields:
  - notification_id (UUID, required)
  - event_id (UUID, required)
  - user_id (UUID, required)
  - data_series_id (string, required)
  - destination_path (string, required)
  - title (string, required)
  - body (string, required)
  - unread_state (enum: `unread` | `read`, required)
  - read_at (timestamp with time zone | null)
  - delivered_at (timestamp with time zone, required)
  - channel (enum: `in_app`, required for this branch)
  - delivery_status (enum: `queued` | `delivered` | `failed` | `suppressed`, required)
- Validation rules:
  - `(event_id, user_id)` is unique to prevent duplicate fan-out rows.
  - `read_at` is required when `unread_state=read`.
  - Only `user_visible` events may produce user notification rows.

## Entity: NotificationUnreadSummary (Read Model)

- Purpose: Lightweight authenticated summary for header badges and quick status checks.
- Fields:
  - user_id (UUID, required)
  - unread_count (integer, required, >= 0)
  - last_notification_at (timestamp with time zone | null)
  - generated_at (timestamp with time zone, required)
- Validation rules:
  - `unread_count` equals count of `UserTrendNotification` rows where `unread_state=unread` for that user.

## Entity: NotificationDropdownFeed (Frontend Read Model)

- Purpose: Compact nav-level projection for recent notification interactions.
- Fields:
  - items (array of up to N `NotificationDropdownItem`, required)
  - unread_count (integer, required, >= 0)
  - has_more (boolean, required)
  - fetched_at (timestamp with time zone, required)
- Validation rules:
  - Items are newest-first and stable across unchanged reads.
  - `unread_count` is sourced from authoritative summary endpoint or equivalent list aggregate.

## Entity: NotificationDropdownItem (Frontend Read Model)

- Purpose: One notification item rendered in top-nav dropdown.
- Fields:
  - notification_id (UUID, required)
  - dataset_id (string, required)
  - title (string, required)
  - body (string, required)
  - destination_path (string, required)
  - unread (boolean, required)
  - delivered_at (timestamp with time zone, required)
- Validation rules:
  - Item identity maps directly to `UserTrendNotification.notification_id`.
  - Read/unread actions must reconcile to backend state when responses return.

## Entity: NotificationPageQueryState (Frontend UI State)

- Purpose: URL/state envelope for notifications management page.
- Fields:
  - page_size (integer, required)
  - cursor (string | null)
  - unread_only (boolean, required)
  - fetch_state (enum: `idle` | `loading` | `loaded` | `error`, required)
- Validation rules:
  - Query-state transitions must preserve deterministic pagination semantics.
  - `error` state is explicit and does not silently clear last known unread summary.

## Entity: DatasetAlertSubscriptionView (Frontend Read Model)

- Purpose: UI-facing projection for dataset follow/unfollow control and subscription list.
- Fields:
  - dataset_id (string, required)
  - is_subscribed (boolean, required)
  - subscribed_at (timestamp with time zone | null)
  - pending_action (enum: `none` | `subscribe` | `unsubscribe`, required)
  - last_error (string | null)
- Validation rules:
  - Only authenticated users can transition subscription state.
  - Unauthenticated interactions route to sign-in prompt and do not mutate backend state.

## Relationships

- One `TrendChangeEvent` can map to many `UserTrendNotification` rows.
- One user has many `UserDatasetSubscription` rows.
- Notification fan-out includes only users with active subscription to the event dataset at event creation time.
- Re-subscribe is forward-only: events emitted before latest `subscribed_at` are ineligible for new delivery.

## State Transitions

- Canonical trend persisted -> compare previous and current directions.
- Qualifying flip (`up <-> down`) -> create `TrendChangeEvent` idempotently.
- Event classification:
  - incremental -> `user_visible` by default
  - historical reprocessing -> `audit_only` by default
- For `user_visible` events, fan-out to active subscriptions:
  - create `UserTrendNotification` rows idempotently
  - initialize as `unread`
- User actions:
  - mark-one-read -> set `unread_state=read`, set `read_at`
  - mark-one-unread -> set `unread_state=unread`, clear `read_at`
  - mark-all-read -> batch set all current unread rows to `read`

## Frontend State Transitions

- Shell mounts -> fetch unread summary and recent dropdown feed for authenticated user.
- Notification bell opened:
  - loading -> dropdown skeleton/loading state
  - loaded with items -> compact list with read-state actions
  - loaded empty -> explicit empty state
  - error -> explicit recoverable error state
- Dropdown or page action invoked (`mark-read`, `mark-unread`, `mark-all-read`):
  - optimistic UI update
  - reconcile unread totals and item state from server response
- Dataset detail follow/unfollow toggled:
  - pending action shown
  - success updates subscription state
  - failure restores prior state and surfaces error

## Determinism and Idempotency Rules

- Reprocessing the same transition must reuse the same event identity boundary (`idempotency_fingerprint`).
- Duplicate retries must not create additional `(event_id, user_id)` notification rows.
- Notification list ordering is deterministic newest-first by `(delivered_at DESC, notification_id DESC)`.
- Pagination cursors are derived from ordering keys so repeated reads of unchanged data return stable pages.
