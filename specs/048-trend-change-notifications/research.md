# Research: In-App Trend Change Notifications (Full-Stack Scope)

## Decision 1: Detect reversals from canonical descriptor transitions in pipeline runtime

- Decision: Detect trend-change events in pipeline runtime immediately after canonical descriptor persistence for an observation, by comparing current canonical direction with prior persisted canonical direction for the same series.
- Rationale: Canonical descriptor persistence is already the authoritative trend seam (`trend_canonical_descriptors`) and avoids repeated read-time derivation.
- Alternatives considered:
  - Derive reversals at backend read time: rejected due to repeated compute and weaker retry semantics.
  - Reuse legacy transition tables as primary source: rejected because current canonical/lookback flow is active contract.

## Decision 2: Emit events only for directional flips `up <-> down`

- Decision: Persist events only when prior and current canonical directions are both non-null and differ (`up` to `down` or `down` to `up`).
- Rationale: Matches product intent and prevents first-available or unavailable noise.
- Alternatives considered:
  - Emit on first available direction: rejected by FR-002.
  - Emit on strength-only changes: rejected as out of scope.

## Decision 3: Historical reprocessing remains audit-only by default

- Decision: Persist historical/backfill reversal events with explicit processing context and visibility classification, but suppress unread fan-out by default.
- Rationale: Preserves traceability without flooding users.
- Alternatives considered:
  - Treat historical and incremental identically: rejected due to user-noise risk.

## Decision 4: Recipient eligibility is authoritative subscription state at event creation

- Decision: Fan-out recipients are active subscriptions at event creation time; new users default to no subscriptions; users manage only their own subscriptions.
- Rationale: Matches clarified policy and ownership constraints.
- Alternatives considered:
  - Broadcast to all users: rejected in clarification.
  - Admin-managed subscriptions for all users: rejected in clarification.

## Decision 5: Re-subscribe is forward-only

- Decision: Re-subscribe does not rehydrate historical unread notifications; only future events are eligible.
- Rationale: Prevents stale backlog replay and aligns with clarified behavior.
- Alternatives considered:
  - Restore all unread on re-subscribe: rejected.
  - Restore bounded historical window: rejected.

## Decision 6: Unread notifications do not auto-expire by age

- Decision: Unread state persists until explicit user action (`mark-read` or `mark-all-read`) or retention archival/removal policy.
- Rationale: Prevents silent loss of potentially important reversals.
- Alternatives considered:
  - Time-based expiration: rejected by clarification.

## Decision 7: Idempotency and dedupe are enforced with database uniqueness

- Decision: Use deterministic uniqueness for reversal events and per-user fan-out rows.
- Rationale: Durable correctness across retries and process restarts.
- Alternatives considered:
  - In-memory dedupe only: rejected as non-durable.
  - Cleanup jobs after duplicate writes: rejected as eventual and brittle.

## Decision 8: Backend API follows existing auth-management route/error patterns

- Decision: Expose notification endpoints in `http_api_server.py` with Bearer-session auth and existing contract-error mapping conventions.
- Rationale: Consistent runtime behavior and lower integration risk.
- Alternatives considered:
  - Separate notification API app: rejected as unnecessary complexity.
  - Unauthenticated read paths: rejected for privacy and ownership rules.

## Decision 9: Frontend uses shell-level HeroUI dropdown in top nav

- Decision: Implement notifications entry in `SiteHeader` utility region as a HeroUI dropdown/popover control with unread badge and recent-notifications list.
- Rationale: `SiteHeader` is the shared shell seam across routes; this ensures consistent cross-page behavior and avoids route-level duplication.
- Alternatives considered:
  - Add notification icon per page header: rejected due to duplication and inconsistency.
  - Add separate global CSS-driven widget outside HeroUI patterns: rejected by UI-system constitution principle.

## Decision 10: Frontend notification management uses dedicated route + shared components

- Decision: Add a dedicated notifications management page and extract reusable notification UI primitives under `apps/frontend/src/components` (dropdown list items, unread badge, list/empty/error blocks).
- Rationale: Maintains shared abstraction discipline and supports desktop/mobile composition.
- Alternatives considered:
  - Keep only dropdown without full-page management: rejected; lacks pagination/filter/read-management parity.
  - Duplicate markup between dropdown and page: rejected by frontend consistency principle.

## Decision 11: Dataset subscription controls belong in dataset detail utility actions

- Decision: Add follow/unfollow alert control to `DatasetDetailHeader` utility actions and support broader subscription management from notifications page.
- Rationale: Users decide alert eligibility in dataset context; `DatasetDetailHeader` already hosts related utility controls.
- Alternatives considered:
  - Place subscription only in account settings: rejected for discoverability.
  - Place subscription only in dropdown: rejected for poor dataset-context clarity.

## Decision 12: Frontend API access patterns reuse existing client and Next.js route proxy style

- Decision: Add typed notification/subscription API client methods and corresponding `apps/frontend/src/app/api/notifications/*` proxy routes mirroring existing auth/discovery proxy patterns.
- Rationale: Keeps server-side token handling centralized and consistent with current architecture.
- Alternatives considered:
  - Direct browser calls to backend for all notification actions: rejected due to inconsistent env/url handling and auth proxy conventions.

## Decision 13: Read-state updates use optimistic UI with authoritative reconciliation

- Decision: Apply optimistic read-state updates in dropdown/page for responsiveness, then reconcile with server responses for authoritative unread totals.
- Rationale: Better UX under interaction-heavy usage while preserving correctness.
- Alternatives considered:
  - Strictly pessimistic updates only: rejected for latency-heavy feel in dropdown interactions.

## Decision 14: Full frontend implementation is in-scope for this branch

- Decision: Implement both backend/pipeline foundations and frontend UX (top-nav icon/dropdown, full management, dataset subscription UI) in this spec.
- Rationale: User explicitly requested full frontend implementation inclusion.
- Alternatives considered:
  - Keep frontend deferred: rejected by latest instruction.

## Repository Seams Confirmed

- Pipeline reversal/persistence seams:
  - `apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py`
  - `apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py`
  - `apps/pipeline/src/orchestration/resources/postgres_trend_repository.py`
- Shared DB seams:
  - `libs/db/src/db/models/trends.py`
  - `libs/db/src/db/repositories/interfaces.py`
  - `libs/db/src/db/repositories/postgres_trend_repository.py`
- Backend API/auth seams:
  - `apps/backend/src/http_api_server.py`
  - `apps/backend/src/query/auth_management_service.py`
- Frontend shell seams:
  - `apps/frontend/src/shell/site-header.tsx`
  - `apps/frontend/src/shell/site-page-frame.tsx`
  - `apps/frontend/src/theme/monochrome-theme.ts`
- Frontend dataset-context seam:
  - `apps/frontend/src/components/discovery/DatasetDetailHeader.tsx`
  - `apps/frontend/src/app/datasets/[id]/page.tsx`
- Frontend API client/proxy seams:
  - `apps/frontend/src/lib/api/auth-management-client.ts`
  - `apps/frontend/src/lib/api/auth-management-types.ts`
  - `apps/frontend/src/app/api/account/navigation/route.ts`
  - `apps/frontend/src/app/api/auth/sessions/route.ts`
- Frontend test seams to extend:
  - `apps/frontend/tests/navbar-interactions.test.tsx`
  - `apps/frontend/tests/navbar-profile-dropdown.test.tsx`
  - `apps/frontend/tests/shell-structure-contract.test.tsx`
  - `apps/frontend/tests/DatasetDetailHeader.test.tsx`

## Planning Outcome

- Full-stack scope is now explicit and includes frontend implementation deliverables.
- No `NEEDS CLARIFICATION` markers remain for planning.
- Design proceeds with concrete shell, page, component, and API seams for frontend delivery.
