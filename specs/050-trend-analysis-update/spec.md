# Feature Specification: Trend Analysis Upgrade

**Feature Branch**: `050-trend-analysis-update`  
**Created**: 2026-04-07  
**Status**: Draft  
**Input**: User description: "The file below contains an early summary of the work I'm planning to do on this repo's trend analysis features. Create an initial spec based on the high-level goals outlined in that document.

@specs/050-trend-analysis-update/research/initial-pre-research-plan.md"

## Clarifications

### Session 2026-04-07

- Q: How should "flat / no meaningful trend" be represented in the canonical output for this feature scope? → A: Introduce an explicit external canonical `flat` direction in this feature.
- Q: With explicit canonical `flat` added, how should reversal events behave in this feature phase? → A: Keep event-triggering directional-only (`up` ↔ `down`), and do not emit reversal events for transitions involving `flat` in this phase.
- Q: For this feature, which canonical contract strategy should planning assume now that `flat` is required externally? → A: Version the external canonical contract in this feature to formally include `flat` and related semantics.
- Q: What rollout behavior should be required for consumers of the versioned canonical contract? → A: Hard cutover; all consumers must switch at once with no compatibility overlap.
- Q: For primary canonical selection, should medium lookbacks be treated as a strict gate or a weighted preference? → A: Weighted preference; medium lookbacks are primary by default, but short/long evidence can win when stronger corroborated evidence exists.
- Q: How should monotonic evidence affect canonical direction selection? → A: Use monotonic evidence as a weighted modifier that adjusts confidence/weight in arbitration, not as an absolute gate.
- Q: When should smoothing be applied? → A: Apply smoothing by default for all eligible series/lookbacks.
- Q: How should seasonal adjustment be scoped across cadences in this phase? → A: Use STL-family seasonal adjustment for weekly and monthly series; allow MSTL for regular sub-daily series with complete/pre-imputed data; defer daily full seasonal adjustment in this phase and keep daily alerts active via non-seasonally-adjusted evaluation.
- Q: How should OLS diagnostic output be handled in external contracts in this phase? → A: Expose OLS diagnostics as first-class fields in canonical and lookback API payloads now.
- Q: Where should OLS diagnostics be shown in the UX in this phase? → A: Show OLS diagnostics only in secondary/expandable trend evidence sections, while keeping the primary trend indicator unchanged.
- Q: How should change-point/regime-shift metadata affect canonical arbitration in this phase? → A: Use change-point/regime-shift metadata only as a limited tie-breaker/context modifier when primary evidence is close or conflicting.
- Q: How should missing/irregular data affect trend classification outcome when core evidence is unreliable? → A: Hard reject irregular series from trend outputs in this phase.
- Q: Where should the new evidence payload be exposed in this phase? → A: Expose evidence payload in detail and as-of endpoints only; keep summary endpoints canonical-only.
- Q: Should strength remain categorical (`mild/strong`) or move to numeric in this phase? → A: Replace categorical strength with numeric confidence/intensity in this phase.
- Q: How should notification copy use numeric strength/confidence in this phase? → A: Keep notifications direction-first, with optional strength/confidence detail only when above a defined threshold.
- Q: For irregular-cadence rejection, should rejection supersede directional outcomes (`up`, `down`, `flat`)? → A: Yes. Rejection supersedes all trend outcomes and no canonical direction is emitted for rejected series.
- Q: When a series is rejected for irregular cadence, how should canonical descriptor be represented in API payloads? → A: Always emit canonical descriptor with `descriptor_state = unavailable` and `reason_code = cadence_irregular_rejected`, with no direction/strength values.
- Q: Should summary endpoints include first-class OLS fields in this phase? → A: No. Only detail and as-of responses include OLS/evidence payloads in this phase; summary remains canonical-only.
- Q: How should general seasonal-adjustment intent and phase-specific cadence scope be represented? → A: Keep both. Use one general principle statement plus one explicit phase-scope statement.
- Q: How should historical persisted trend descriptors/events be handled at hard cutover? → A: Fresh-start local development data: reset the database, remove prior trend/notification data, and treat the new contract as the only active baseline.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Stable Current Trend Signal (Priority: P1)

As a data consumer viewing a dataset, I want the current trend label to reflect meaningful movement rather than endpoint noise so I can trust whether the series is up, down, or effectively flat and understand trend strength.

**Why this priority**: Current trend direction is operationally critical because it drives both user interpretation and reversal alerts.

**Independent Test**: Can be fully tested by evaluating representative noisy and smooth series and verifying the resulting current trend direction and strength are more stable and consistent with observed movement.

**Acceptance Scenarios**:

1. **Given** a series with short-term noise but a consistent medium-horizon upward movement, **When** the system evaluates trend evidence, **Then** the canonical direction is reported as upward and does not flip due to isolated endpoint spikes.
2. **Given** a series with no meaningful directional movement, **When** the system evaluates trend evidence, **Then** the canonical output uses the agreed no-meaningful-trend representation and does not assert a false up/down direction.

---

### User Story 2 - Reliable Historical As-Of Trend Inspection (Priority: P2)

As an analyst inspecting history, I want trend snapshots to remain available for each observation date and lookback so I can review what trend evidence existed at any prior point in time.

**Why this priority**: Historical traceability is required for explainability, auditability, and confidence in trend-based product behavior.

**Independent Test**: Can be fully tested by selecting historical observations across multiple series and confirming the system returns consistent applicability status, snapshot evidence, and a single canonical descriptor for each as-of point.

**Acceptance Scenarios**:

1. **Given** a series with sufficient history for multiple windows, **When** an as-of observation is requested, **Then** the response includes applicable and inapplicable lookbacks with explicit reasons and includes canonical selection derived only from applicable evidence.
2. **Given** a series with limited history, **When** an as-of observation is requested, **Then** unsupported windows are marked inapplicable and the system still returns the best available canonical descriptor outcome.

---

### User Story 3 - Lower-Noise Reversal Notifications (Priority: P3)

As a subscribed user, I want reversal notifications to reflect meaningful directional changes instead of frequent oscillations so that alerts remain useful and actionable.

**Why this priority**: Notification trust depends on stable event semantics; high churn reduces product value even if trend calculations are statistically improved.

**Independent Test**: Can be fully tested by replaying historical and incremental runs and comparing event generation behavior before and after the upgrade to confirm reduced spurious reversals without missing clear directional changes.

**Acceptance Scenarios**:

1. **Given** an incremental run where canonical direction meaningfully changes from up to down (or down to up), **When** trend transition processing occurs, **Then** exactly one qualifying reversal event is created and fan-out behavior remains idempotent.
2. **Given** a backfill or replay run, **When** reversal candidates are evaluated, **Then** visibility mode follows existing policy and does not generate unintended user-visible noise.

### Edge Cases

- A series has enough points overall but large gaps or irregular cadence that reduce trend reliability.
- Multiple adjacent lookbacks disagree on direction; short windows indicate reversal while medium windows remain stable.
- Long-horizon evidence conflicts with recent windows during regime shift periods.
- A new observation arrives with the same observation date but later reporting time and changes as-of ordering.
- A series transitions from unavailable directional output to available directional output (and vice versa).

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST preserve the existing multi-stage trend flow (cadence/applicability, per-lookback evaluation, canonical selection, persistence/exposure, and transition eventing) while upgrading trend evidence quality within that flow.
- **FR-002**: The system MUST continue evaluating the full configured lookback catalog for each eligible observation and MUST record applicability status and reason for every catalog lookback.
- **FR-003**: The system MUST compute per-lookback trend evidence using a robust full-window method that reduces endpoint sensitivity compared with simple endpoint percent-change logic.
- **FR-004**: The system MUST apply preprocessing by default for eligible series and MUST record preprocessing mode/status so evidence remains interpretable.
- **FR-005**: The system MUST ensure canonical selection is based on applicable lookbacks only and MUST prioritize medium-horizon agreement over isolated very-short-window reversals unless corroborating evidence exists.
- **FR-006**: The system MUST preserve a single canonical descriptor outcome per observation and MUST keep compatibility with existing downstream consumers unless explicitly versioned in scope.
- **FR-007**: The system MUST retain as-of historical trend inspection behavior so prior observations can be evaluated with the same canonical-selection rules used for current observations.
- **FR-008**: The system MUST keep reversal-event triggering directional-only (`up` ↔ `down`) in this phase, MUST NOT emit reversal events for transitions involving `flat`, and MUST avoid introducing materially higher alert churn under comparable data conditions.
- **FR-009**: The system MUST preserve idempotent trend-change event creation and notification fan-out behavior under repeated or replayed processing.
- **FR-010**: The system MUST distinguish user-visible versus audit-only trend transition outcomes according to run context and keep those semantics stable across the upgrade.
- **FR-011**: The system MUST expose enough descriptive metadata in trend outputs to explain why a canonical direction was selected or unavailable without requiring internal implementation knowledge.
- **FR-012**: The system MUST define explicit contract-transition rules for trend descriptor, snapshot, and notification payload semantics; for this prototype phase, transition uses hard cutover with local data reset and no legacy payload fallback.
- **FR-013**: The system MUST treat lookback horizons with differentiated canonical influence using a weighted preference model: shortest windows as corroborated early-signal evidence, medium windows as primary default evidence, and longest windows as contextual or tie-break evidence when corroboration is stronger.
- **FR-014**: The system MUST preserve the ability to compute trend snapshots for the current observation and all prior observations with sufficient data, using consistent as-of ordering rules.
- **FR-015**: The system MUST represent no-meaningful-trend outcomes as an explicit canonical `flat` direction and apply this representation consistently across compute outputs, persisted descriptors, and API-facing trend payloads.
- **FR-016**: The system MUST use a versioned external canonical contract in this feature phase to formally include `flat` and its related semantics, with local-reset cutover as the migration posture for this prototype.
- **FR-017**: The system MUST include replay and backfill comparison criteria to measure historical divergence from current trend and notification behavior prior to rollout.
- **FR-018**: The system MUST prioritize incremental and testable rollout phases that allow side-by-side comparison with the current method before full adoption.
- **FR-019**: The system MUST enforce a hard cutover to the versioned canonical contract, requiring all consumers to adopt the new contract in the same release without dual-contract compatibility overlap.
- **FR-020**: The system MUST use a robust slope-based method (Theil-Sen) as the primary per-lookback trend signal and treat ordinary least-squares slope as optional diagnostic context rather than the primary decision signal.
- **FR-021**: The system MUST use monotonic-trend evidence scoring using a rank-based method (Kendall tau or Mann-Kendall style significance) as a weighted modifier that strengthens or weakens per-lookback confidence during canonical arbitration, without acting as an absolute gate by itself.
- **FR-022**: The system MUST apply smoothing by default for eligible series using lightweight methods (EWMA and/or robust rolling median style smoothing) before per-lookback scoring, with explicit exception handling only for ineligible or unsupported cases.
- **FR-023**: As a general rule, the system MUST support explicit decomposition-based seasonal adjustment for eligible regular-cadence series, with clear fallback to non-seasonally-adjusted scoring when reliability conditions are not met; phase-specific cadence policy in FR-031 takes precedence where more specific.
- **FR-024**: The system MUST generate change-point/regime-shift indicators as additive explanatory metadata and may use them only as limited tie-breaker/context modifiers when primary evidence is close or conflicting, without replacing canonical direction selection. For this phase, "close" means the absolute difference between top-two canonical candidate confidence scores is <= 0.05, and "conflicting" means those candidates imply different directions.
- **FR-025**: The system MUST define a single canonical arbitration output used across all downstream surfaces, where multiple internal statistical measures are combined into one final canonical descriptor for UI and alerting use.
- **FR-026**: The system MUST define a standard evidence payload for lookback snapshots and canonical traceability that captures which measure family drove the decision, confidence score, and preprocessing mode used; this requirement defines payload content only, while exposure scope is defined in FR-036.
- **FR-027**: The system MUST propagate canonical-contract changes end-to-end in the same release across compute outputs, persistence, backend query contracts, frontend API types/normalizers, trend indicator components, and notification event processing.
- **FR-028**: The system MUST preserve the existing summary/detail trend UX pattern (single trend chip/label plus lookback snapshot view) while updating copy/states to support `flat` and upgraded evidence semantics.
- **FR-029**: The system MUST define endpoint-level compatibility expectations so every discovery endpoint that emits canonical descriptors returns the same versioned descriptor semantics and does not mix old/new direction enums in one release.
- **FR-030**: The system MUST ensure notification and event contracts remain aligned with canonical semantics by explicitly defining how `flat` and non-directional evidence are handled in event eligibility, stored event fields, and user-visible notification payloads.
- **FR-031**: The system MUST scope seasonal adjustment by cadence in this phase: weekly/monthly use STL-family adjustment; regular sub-daily series may use MSTL when data completeness standards are met; daily series use non-seasonally-adjusted scoring in this phase while remaining fully eligible for canonical direction and alerting.
- **FR-032**: The system MUST define explicit phase-gate criteria for introducing daily seasonal adjustment in a later phase, including replay-delta review and alert-stability thresholds. Minimum gate criteria are: (a) daily replay canonical-direction divergence <= 5% versus non-seasonally-adjusted baseline on approved benchmark sets, (b) false-positive reversal-event increase <= 10% on incremental simulations, and (c) no endpoint contract incompatibilities in discovery payload validation.
- **FR-033**: The versioned external trend descriptor contracts MUST expose OLS diagnostic outputs as first-class fields for canonical and per-lookback payloads on detail and as-of responses in this phase, with clear semantics and presence rules; summary responses remain canonical-descriptor-only.
- **FR-034**: The frontend trend UX MUST treat OLS diagnostics as supplementary detail, displaying them only in secondary or expandable trend evidence sections while preserving the single canonical trend indicator as the primary experience.
- **FR-035**: The system MUST hard reject irregular-cadence series from trend classification outputs in this phase, with explicit reason codes and no canonical direction emission for rejected series.
- **FR-036**: The versioned evidence payload (including OLS diagnostics, monotonic evidence context, and preprocessing metadata) MUST be exposed on detail and observation-as-of responses in this phase, while summary/list responses remain canonical-descriptor-only.
- **FR-037**: The versioned canonical and lookback contracts MUST replace categorical `strength` labels with a numeric `confidence_score` representation using a 0.00-1.00 scale (two-decimal display precision), with null permitted only when `descriptor_state = unavailable`; scale semantics, nullability rules, and interpretation guidance MUST be consistent across compute, persistence, backend, and frontend.
- **FR-038**: User-visible notification copy MUST remain direction-first in this phase and may include `confidence_score` only when `confidence_score >= 0.70`; this threshold and formatting rules MUST be applied consistently across backend payload generation and frontend rendering.
- **FR-039**: Rejection precedence MUST supersede all directional outcomes (`up`, `down`, `flat`): when a series is rejected for irregular cadence, canonical direction is not emitted and downstream event/notification eligibility is evaluated as non-directional.
- **FR-040**: For rejected series, API payloads MUST still emit canonical descriptor objects using `descriptor_state = unavailable` and `reason_code = cadence_irregular_rejected`, with direction and strength omitted/null.
- **FR-041**: For this prototype phase, rollout MUST use a fresh-start local environment baseline: existing local persisted trend/event/notification data is reset, and only the new versioned contract semantics are supported after restart. The reset procedure MUST be executable and verified in local validation by demonstrating (a) legacy trend descriptor rows are absent after reset, (b) new v2 descriptors are repopulated from a clean run, and (c) event/notification tables contain only post-reset records.

### Planned Trend Analysis Changes

The upgrade focuses on improving how trend evidence is computed and selected inside the trend-analysis library while preserving the existing architecture around it.

- **Signal robustness upgrade**: Replace endpoint-only trend judgments with full-window trend evidence so one noisy point is less likely to dominate direction and strength.
- **Signal robustness upgrade**: Use Theil-Sen slope as the default per-lookback trend signal, with ordinary least-squares slope retained only as secondary diagnostic context.
- **Monotonic evidence support**: Use rank-based monotonic evidence (Kendall tau or Mann-Kendall style significance) to improve confidence handling for noisy but directional series.
- **Preprocessing stage**: Add a governed preprocessing step that runs by default for eligible series to stabilize noise and better separate recurring seasonal movement from underlying direction.
- **Smoothing methods**: Use lightweight smoothing options such as EWMA and robust rolling median style smoothing as the default preprocessing behavior for eligible series.
- **Seasonality handling upgrade**: Move from heuristic seasonality flags to explicit decomposition-based seasonal adjustment, with weekly/monthly as first-phase defaults and daily seasonal adjustment deferred to a later gated phase.
- **Sub-daily handling**: Allow MSTL-style adjustment for regular sub-daily series when data completeness and recurring multi-season structure requirements are satisfied.
- **Canonical arbitration rebalance**: Keep all lookbacks for evidence, but rebalance canonical selection so short windows act as early signals, medium windows are primary direction evidence, and long windows provide context.
- **No-meaningful-trend handling**: Define a consistent representation for weak/flat conditions so consumers can distinguish directional trends from insufficient or non-meaningful movement.
- **Additive regime context**: Introduce change-point/regime-shift detection as explanatory metadata in early phases, with only limited tie-breaker/context influence when primary evidence is close or conflicting.
- **Operational stability protection**: Keep reversal-event and notification semantics stable during the first rollout phase, and introduce richer behavior only after stability is validated.

### Contract Propagation to UX

The upgrade introduces more than one internal trend measure, but the product experience must remain coherent and consistent across backend and frontend surfaces.

- **Single outward decision**: Internal measures are combined into one canonical descriptor that remains the primary trend shown in list/detail UI and used by alerting workflows.
- **Consistent descriptor contract**: Summary, detail, and observation-as-of payloads use the same versioned canonical semantics (including `flat`) so UI state handling stays predictable.
- **Evidence without overload**: Additional measure outputs are exposed as structured evidence metadata for traceability and debugging, not as raw statistical payloads that the default UX must interpret.
- **UI continuity**: Existing trend indicator patterns remain (chip/label and lookback snapshots), with only targeted copy/state updates needed for `flat` and enhanced evidence explanations.
- **Notification alignment**: Reversal-event generation and notification copy continue to use explicit contract rules so users are not exposed to contradictory trend states across pages and alerts.

### Key Entities _(include if feature involves data)_

- **Observation Series**: Ordered historical values for one dataset metric, including observation date and reporting timestamp used for as-of resolution.
- **Lookback Applicability Record**: Per-observation, per-lookback status indicating whether a window can be evaluated and, if not, why.
- **Lookback Trend Snapshot**: Per-observation, per-lookback trend evidence payload containing direction, strength/evidence interpretation, and supporting metadata.
- **Canonical Trend Descriptor**: Single selected trend state for an observation (`up`, `down`, or `flat`) used for summary/detail display and as the source signal for transition evaluation.
- **Trend Evidence Metadata**: Structured explanation payload identifying dominant evidence family, confidence/evidence level, and preprocessing context behind snapshot/canonical outcomes.
- **OLS Diagnostic Fields**: Versioned contract fields representing ordinary least-squares diagnostic outputs for canonical and per-lookback trend results, intended as supplementary evidence.
- **Trend Change Event**: Persisted directional transition record representing a qualifying canonical reversal and carrying visibility mode.
- **User Trend Notification**: User-facing delivery record derived from eligible trend change events and subscription rules.

## Assumptions

- Existing lookback catalog values remain unchanged for this phase; improvements focus on evidence weighting and arbitration behavior.
- The canonical direction contract is expanded in this feature phase to include an explicit `flat` direction.
- Alert-event semantics remain directional-only in this phase; transitions involving `flat` are descriptive only and do not trigger reversal notifications.
- Upgrade rollout will compare new versus current behavior on historical data before broad enablement.
- When trend evidence is weak or conflicting, conservative non-directional outcomes are preferable to unstable directional claims.
- Frontend changes are expected to be minimal and primarily limited to label or explanatory text updates when needed to reflect improved trend semantics.
- Change-point or regime-shift output is treated as additive explanatory metadata in initial rollout phases, not a replacement for canonical direction.
- Daily series do not receive full seasonal adjustment in this phase; eligible daily series continue through non-seasonally-adjusted evaluation, while irregular daily series follow rejection precedence.
- Rejected irregular-cadence series still emit canonical descriptor payloads as unavailable with explicit rejection reason codes.
- This feature assumes a local-dev-only reset migration posture: historical local data is disposable and not preserved across cutover.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In backtesting against representative historical series, the upgraded method reduces short-horizon direction flip frequency by at least 30% compared with the current method while preserving detection of clear directional periods.
- **SC-002**: For a curated benchmark set with expected directional outcomes, at least 90% of canonical direction results match reviewer-approved expectations.
- **SC-003**: For observations with sufficient history, 100% of configured lookbacks return an explicit applicability status, and 100% of applicable lookbacks return a snapshot evidence payload.
- **SC-004**: In incremental processing trials, false-positive reversal notifications decrease by at least 25% versus baseline while true directional reversals continue to generate events within one processing cycle.
- **SC-005**: For all tested as-of observation requests, canonical descriptor and snapshot outputs are reproducible across repeated runs with no unexplained divergence.
- **SC-006**: For historical replay comparisons, at least 95% of event records remain idempotent under repeated processing and no duplicate user notification deliveries are created.
- **SC-007**: Stakeholder review confirms the selected canonical contract strategy and rollout phases before implementation, with no unresolved scope-level decisions.
- **SC-008**: At release cutover, 100% of in-scope consumers successfully read the versioned canonical contract with no fallback to legacy contract shape.
- **SC-009**: In contract-validation tests across all discovery responses that include trend descriptors, 100% of canonical descriptor payloads conform to one versioned schema and include consistent direction semantics (`up`, `down`, `flat`, or explicitly unavailable).
- **SC-010**: In UX validation for list/detail and notifications, users observe no contradictory trend states for the same dataset at the same as-of point across chip labels, detail descriptors, and eligible alert messages.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and automated test gates without suppressions, bypasses, or workaround-only code, and the full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or above 90% in affected projects, and can satisfy the commit-time coverage stop rule (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack, or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes, provenance/timestamp impacts, and trend-alert reliability safeguards are defined. (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be created or updated in the same change for any impacted behavior, contracts, setup, or runbooks, including AGENTS.md when repository structure/workflows/tooling change. (Yes)
- **CA-006 Configuration Integrity**: Any new service or pipeline component that requires credentials or external API keys will fail hard (exception/non-zero exit/job-level failure) when those variables are absent - no soft outcome recording, no silent swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source for any Docker Compose service that requires secrets. (N/A)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI components, Tailwind utilities, and shared abstractions in `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate one-off component patterns or new local CSS without a documented exception. (Yes)
