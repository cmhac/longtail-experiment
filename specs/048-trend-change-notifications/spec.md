# Feature Specification: In-App Trend Change Notifications

**Feature Branch**: `[048-trend-change-notifications]`  
**Created**: 2026-04-05  
**Status**: Draft  
**Input**: User description: "we can start with in app notifications only for now, but it should be planned for future implementation of other notification channels including email and slack in a future branch." and follow-up direction to include full frontend implementation for notification UX in this spec.

## Assumptions

- Initial release delivers in-app notifications only.
- A trend-change notification is generated only when a dataset's canonical trend direction changes from `up` to `down` or from `down` to `up`.
- Initial recipient scope is users explicitly subscribed to a dataset.
- New users start with no default dataset subscriptions.
- Unread notifications do not auto-expire; users clear them manually, or retention policy applies archival/removal.
- Historical reprocessing/backfill is recorded for auditability but does not create new unread in-app notifications by default.
- Future channels (email, Slack) are planned through channel-ready event modeling but are out of scope for this branch.

## Clarifications

### Session 2026-04-05

- Q: Who should receive each in-app trend reversal notification? → A: Only users who explicitly follow/subscribe to a dataset.
- Q: What should the default subscription behavior be for new users? → A: No default subscriptions; users must explicitly follow datasets.
- Q: Who is allowed to create/remove dataset subscriptions? → A: Each user manages only their own subscriptions.
- Q: What should happen when a user unsubscribes and later re-subscribes to a dataset? → A: Do not restore past notifications; only new events after re-subscribe.
- Q: Should unread notifications expire from the in-app inbox automatically? → A: No auto-expiry; keep until user reads or retention policy archive/removal applies, and provide an easy bulk-clear action.

### Session 2026-04-06

- Q: Should this branch include full frontend notification implementation? → A: Yes; include top-nav notification icon, recent-notifications dropdown, read/unread management interactions, and dataset alert subscription controls in the UI.

## Full-Stack Scope Coverage

- **Trend processing layer**: Detect reversal events during canonical trend updates and label each event with processing context so incremental processing and historical reprocessing are distinguishable.
- **Persistence layer**: Store reversal events, user-addressed in-app notifications, per-user read-state transitions, and delivery/audit status as durable records.
- **Backend service layer**: Expose authenticated notification retrieval and read-state actions, including unread summary access and dataset-linked notification payloads.
- **Frontend experience layer**: Implement authenticated notification UX end-to-end, including top-nav icon + unread badge, recent-notifications dropdown, full notification management surfaces (read/unread and clear-all unread), dataset alert subscription controls, and resilient empty/loading/error states.
- **Operations and documentation layer**: Define support/audit workflows for replay and troubleshooting and document how this release prepares for future email/Slack channels.

## Out of Scope

- Sending notifications through email in this branch.
- Sending notifications through Slack in this branch.
- User-managed channel preferences beyond in-app delivery.
- Digest scheduling or batched summary notifications.

## User Scenarios & Testing _(mandatory)_

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Detect and Record Trend Reversals (Priority: P1)

As a product stakeholder, I need the system to reliably detect when a dataset trend direction reverses so I can be alerted to meaningful changes instead of scanning every chart manually.

**Why this priority**: Without reliable reversal detection, there is no notification value to deliver in any channel.

**Independent Test**: Can be fully tested by processing new trend updates where canonical direction changes and verifying exactly one reversal event is recorded for each qualifying change.

**Acceptance Scenarios**:

1. **Given** a dataset with a prior canonical direction of `up`, **When** a new canonical direction of `down` is recorded, **Then** one trend-change event is created with prior and new direction metadata.
2. **Given** a dataset with no prior canonical direction, **When** its first canonical direction becomes available, **Then** no reversal event is created.
3. **Given** a previously processed observation is retried, **When** processing runs again for the same effective direction change, **Then** no duplicate reversal event is created.

---

### User Story 2 - In-App Notification Inbox for Reversals (Priority: P2)

As an authenticated user, I want to see reversal notifications for datasets I follow so I can quickly review what changed and navigate to the affected dataset.

**Why this priority**: This is the first user-facing delivery channel and provides immediate value from detected reversals.

**Independent Test**: Can be fully tested by generating reversal events, verifying top-nav unread badge and dropdown recents, opening the full in-app notifications management view, and confirming read-state updates and navigation.

**Acceptance Scenarios**:

1. **Given** unread reversal notifications exist, **When** a user opens their notifications, **Then** they see newest-first items showing dataset context and direction change summary.
2. **Given** a notification is unread, **When** the user marks it read, **Then** unread counts and item state update consistently.
3. **Given** a notification references a dataset reversal, **When** the user selects it, **Then** they are taken to the corresponding dataset detail context.
4. **Given** a user unsubscribes and later re-subscribes to a dataset, **When** they return to their notifications, **Then** only reversal events created after re-subscribe are eligible for delivery.
5. **Given** multiple unread notifications exist, **When** a user chooses clear-all unread, **Then** all unread items are marked read in one straightforward action.
6. **Given** an authenticated user has unread notifications, **When** they view the top navigation, **Then** a notifications icon displays an unread indicator consistent with backend unread summary.
7. **Given** an authenticated user opens the top-nav notifications control, **When** recent notifications are available, **Then** a dropdown shows a concise newest-first list with read-state affordances and a link to full notifications management.
8. **Given** an unauthenticated user opens the notifications control, **When** they are not signed in, **Then** the dropdown presents a sign-in action instead of private notification content.
9. **Given** a notification was previously marked read, **When** a user marks it unread from supported notification management controls, **Then** unread totals and item state update consistently.

---

### User Story 3 - Manage Dataset Alert Subscriptions in UI (Priority: P2)

As an authenticated user, I want to subscribe or unsubscribe to dataset reversal alerts directly in the UI so I can control which datasets generate in-app notifications.

**Why this priority**: Subscription state controls notification eligibility and must be accessible without backend-only workflows.

**Independent Test**: Can be fully tested by toggling subscription state from dataset-facing UI controls and verifying backend subscription changes and resulting notification eligibility.

**Acceptance Scenarios**:

1. **Given** an authenticated user on a dataset detail page, **When** they choose follow/unfollow alerts, **Then** the subscription state updates and UI feedback confirms the result.
2. **Given** a user has multiple subscriptions, **When** they open notification subscription management in UI, **Then** they can review and remove their own subscriptions only.
3. **Given** the user is not authenticated, **When** they attempt to follow dataset alerts, **Then** the UI prompts sign-in and does not create a subscription.

---

### User Story 4 - Channel-Ready Notification Foundation (Priority: P3)

As a product owner, I want today's notification architecture to support future channels so email and Slack can be added later without redefining core reversal semantics.

**Why this priority**: It protects future roadmap velocity while keeping current branch scope focused on in-app delivery.

**Independent Test**: Can be fully tested by verifying notification events preserve channel-agnostic payload semantics and in-app delivery continues unchanged.

**Acceptance Scenarios**:

1. **Given** a reversal event is recorded, **When** channel configuration evolves in future branches, **Then** the event payload remains valid without redefining reversal meaning.
2. **Given** in-app is the only enabled channel in this release, **When** events are created, **Then** delivery status reflects in-app outcomes without requiring external-channel setup.

---

### User Story 5 - Auditable End-to-End Notification Traceability (Priority: P3)

As an operator or support stakeholder, I want to trace how a trend reversal became a user notification so incidents can be investigated quickly and historical processing can be explained.

**Why this priority**: Notification trust depends on reliable supportability across processing, storage, delivery, and user state.

**Independent Test**: Can be fully tested by selecting a known reversal, verifying its processing context and event history, and confirming user-visible notification/read-state records match expected behavior.

**Acceptance Scenarios**:

1. **Given** a user-visible reversal event exists, **When** support reviews audit records, **Then** they can link dataset reversal details to user notification and read-state lifecycle.
2. **Given** historical reprocessing runs, **When** audit records are reviewed, **Then** historical-only events are distinguishable from user-visible notifications.

---

### Edge Cases

- A dataset reverses direction multiple times in a short period; each distinct reversal must be represented once and in correct chronological order.
- Canonical trend descriptor becomes unavailable after being available; this does not count as an up/down reversal.
- Backfill/reclassification updates historical records; user-facing unread notifications are not newly generated by default for historical changes.
- Late-arriving data alters prior trend history; event ordering and user-visible timestamps remain deterministic.
- User account deactivation occurs after notifications exist; existing records remain auditable and inaccessible through inactive sessions.
- A user subscribes to a dataset after prior reversals; only in-scope notifications after subscription are delivered.
- A new user who has not subscribed to any dataset sees no reversal notifications until they follow at least one dataset.
- Temporary service failures occur while generating per-user notifications; event history remains intact and user delivery state reflects incomplete delivery without duplicating records.
- A user attempts to modify another user's subscriptions; the action is denied and does not alter recipient eligibility.
- A user unsubscribes and later re-subscribes to the same dataset; previously generated notifications are not rehydrated into unread state.
- Notifications remain unread for long periods; they are still visible until user action or retention-based archival/removal.
- The top-nav dropdown is opened while summary/list requests are still loading; UI must not show stale negative unread counts or contradictory badge/dropdown states.
- A user rapidly toggles read/unread actions from dropdown and full list; final UI state must converge to server-confirmed state without duplication.
- A user attempts to manage subscriptions for another account through crafted client input; backend denial must surface as non-destructive UI error.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST detect a trend-change event when a dataset's canonical trend direction transitions from `up` to `down` or from `down` to `up`.
- **FR-002**: System MUST NOT create a trend-change event when canonical direction is first established from a previously unavailable state.
- **FR-003**: System MUST NOT create a trend-change event when canonical direction remains unchanged.
- **FR-004**: System MUST persist each trend-change event with dataset identity, prior direction, new direction, effective trend observation date, and event creation timestamp.
- **FR-005**: System MUST enforce idempotency so retries or reprocessing of the same transition do not create duplicate events.
- **FR-006**: System MUST classify events as user-visible or historical-audit-only according to processing context, with historical reprocessing defaulting to audit-only visibility.
- **FR-007**: System MUST create in-app notification records only for users who are explicitly subscribed to the affected dataset at the time a user-visible trend-change event is created.
- **FR-008**: System MUST expose notification data with stable newest-first ordering and deterministic pagination semantics for unchanged data.
- **FR-009**: System MUST provide unread/read state per user notification item.
- **FR-010**: Users MUST be able to mark individual notifications as read.
- **FR-011**: Users MUST be able to mark all currently unread notifications as read through a single, easy-to-find action.
- **FR-012**: Each in-app notification MUST include a user-action path to the affected dataset detail context.
- **FR-013**: System MUST enforce access control so users can only retrieve and modify their own notification read state.
- **FR-014**: System MUST retain notification records for at least 365 days before archival/removal policies can remove those records.
- **FR-015**: System MUST expose event metadata sufficient for future multi-channel delivery without changing reversal-event semantics.
- **FR-016**: System MUST track delivery outcome states for enabled channels, with in-app channel active in this release and external channels disabled by default.
- **FR-017**: System MUST preserve a complete auditable trail of reversal events, including suppressed historical events and user-visible events.
- **FR-018**: System MUST provide consistent unread-count summaries across all in-app surfaces that display notification status.
- **FR-019**: System MUST record processing context for each reversal event so incremental updates and historical reprocessing are explicitly distinguishable.
- **FR-020**: System MUST maintain immutable reversal-event history separate from mutable per-user notification read state.
- **FR-021**: System MUST provide authenticated unread-notification summaries without requiring users to fetch full notification lists.
- **FR-022**: System MUST preserve deterministic notification ordering and stable pagination behavior for repeated reads of unchanged data.
- **FR-023**: System MUST return contract-valid empty-result payloads and explicit error envelopes so clients can render reliable empty/loading/failure state transitions.
- **FR-024**: System MUST ensure account status changes (activation/deactivation) are consistently reflected in notification access and delivery behavior.
- **FR-025**: System MUST define and document operational procedures for replay handling, incident triage, and reversal-to-notification audit tracing.
- **FR-026**: System MUST define channel-agnostic notification event semantics so future email and Slack channels can be added without changing in-app behavior contracts.
- **FR-027**: System MUST support explicit user subscription state per dataset and use that state as the notification-recipient eligibility source.
- **FR-028**: System MUST default new users to an empty subscription set and require explicit user action to follow datasets.
- **FR-029**: System MUST allow users to create and remove only their own dataset subscriptions; cross-user subscription management is out of scope for this release.
- **FR-030**: System MUST treat re-subscription as forward-only eligibility, so notifications created before the latest re-subscribe timestamp are not newly delivered.
- **FR-031**: System MUST NOT auto-expire unread notifications solely due to age; unread state persists until user action or retention-based archival/removal.
- **FR-032**: Frontend MUST display a notifications control in top navigation for all pages using the shared site shell.
- **FR-033**: Frontend MUST show unread badge state on the top-nav notifications control for authenticated users using backend unread summary.
- **FR-034**: Frontend MUST provide a top-nav dropdown with recent notifications, read-state affordances, and a clear path to full notification management.
- **FR-035**: Frontend MUST provide a dedicated notification management surface that supports UI list pagination, unread filtering, single mark-read, and clear-all unread.
- **FR-036**: Frontend MUST provide dataset-level subscription controls in dataset-facing UI so users can follow/unfollow reversal alerts without leaving context.
- **FR-037**: Frontend MUST provide authenticated subscription management UI for reviewing and removing existing dataset subscriptions.
- **FR-038**: Frontend MUST present explicit empty, loading, and error states for notification dropdown, notification management, and subscription controls.
- **FR-039**: Frontend MUST preserve read-state consistency between dropdown and full management views after user actions.
- **FR-040**: Frontend MUST route unauthenticated notification and subscription actions to sign-in flow without exposing private data.
- **FR-041**: Users MUST be able to mark an individual read notification back to unread where notification management controls support that action.

### Key Entities _(include if feature involves data)_

- **Trend Change Event**: A canonical reversal record representing one direction flip for a dataset; includes prior/new direction, effective date, visibility classification, and lifecycle status.
- **User Notification**: A user-addressed in-app item derived from a trend-change event; includes display summary, destination context, read state, and timestamps.
- **Notification Delivery State**: Channel-specific status attached to an event or notification indicating whether delivery was queued, delivered, failed, or intentionally suppressed.
- **Notification Channel Policy**: Configuration-level representation of which channels are enabled; in-app enabled now, email/Slack reserved for future branches.
- **Notification Read Summary**: Per-user aggregate state used for unread counts and inbox indicators.
- **Processing Context Marker**: Event-level classification that identifies whether the originating reversal came from incremental processing or historical reprocessing.
- **User Dataset Subscription**: Relationship describing which datasets a user follows and is therefore eligible to receive reversal notifications for.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 99% of eligible trend reversals appear in users' in-app notification inbox within 5 minutes of trend processing completion.
- **SC-002**: 100% of retried processing runs for the same reversal transition produce no additional duplicate user-visible notifications.
- **SC-003**: 95% of users can open a notification and reach the relevant dataset context in 2 interactions or fewer.
- **SC-004**: Unread notification counts match underlying item state with at least 99.9% consistency during normal usage.
- **SC-005**: In an acceptance review sample of at least 30 reversal notifications, at least 90% must receive an actionable score of 4 or 5 on a 5-point reviewer rubric.
- **SC-006**: Support stakeholders can trace a sampled reversal notification from reversal event to user read state in under 5 minutes for 95% of audited cases.
- **SC-007**: 100% of impacted stack areas (trend processing, persistence, backend services, frontend surfaces, and operational documentation) have at least one acceptance scenario and one functional requirement in this specification.
- **SC-008**: 95% of authenticated users can open the top-nav dropdown, review recent notifications, and reach full notifications management within 2 interactions.
- **SC-009**: 95% of authenticated users can follow or unfollow dataset alerts from dataset UI in 1 interaction after control visibility.
- **SC-010**: Top-nav unread badge and full-notification unread totals remain consistent within one refresh cycle for 99.9% of sampled interactions.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code, and the
  full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before
  commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects, and can satisfy the commit-time coverage stop rule
  (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
- **CA-006 Configuration Integrity**: Any new service or pipeline component that requires
  credentials or external API keys will fail hard (exception/non-zero exit/job-level
  failure) when those variables are absent — no soft outcome recording, no silent
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source
  for any Docker Compose service that requires secrets. (N/A)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI
  components, Tailwind utilities, and shared abstractions in
  `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate
  one-off component patterns or new local CSS without a documented exception.
  (Yes)
