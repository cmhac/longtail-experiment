# Briefing for AI Coding Agent: Technical Planning for Trend Analysis Upgrade

## Purpose

You are being asked to do **technical planning**, not implementation, for an upgrade to an existing trend-analysis subsystem.

The product goal is to let a user inspect a dataset or time series and quickly get a sensible summary of how it is trending, such as:

- up
- down
- flat / no meaningful trend
- Strength/velocity

The current implementation is an early prototype that uses overly-simplistic rule-based trend definitions. We are open to changing internals substantially, but we would prefer to **preserve the broad shape of the existing architecture** where possible.

The planning task is therefore:

1. understand the current system shape,
2. identify its current weaknesses,
3. understand the proposed statistical methods to replace the existing heuristics
4. understand implementation complexity and architectural impact,
5. interactively make design choices with the user to prepare to codify this redesign as a formal spec

---

## High-level product constraint

We want better trend identification, but we do **not** want to incur major architectural churn unless there is a strong reason.

Working preference:

- improve statistical robustness,
- keep the current multi-lookback pattern, allowing lookback trends for the current observation and all prior obesrevations with sufficient data
- preserve existing downstream concepts where practical,
- make incremental changes that can be tested and compared against the current system.

The ultimate goal is to make most of these changes internal, preserving the frontend as much as possible. however small changes to labels/ui are acceptable to communicate the improved trend data we will have.

---

## Current system: conceptual model

The current system appears to operate at three levels:

1. **raw observations**
2. **per-lookback evaluations / snapshots**
3. **canonical single current trend state**

At a high level, the system currently does this:

1. ingest ordered observations for a series,
2. infer or otherwise determine cadence characteristics,
3. evaluate a fixed catalog of lookback intervals,
4. mark each lookback as applicable or inapplicable,
5. compute per-lookback trend outputs for applicable lookbacks,
6. select one canonical trend descriptor from the applicable candidates,
7. persist and expose both snapshot-level and canonical trend outputs,
8. detect canonical-direction reversals and convert qualifying reversals into alert events and user notifications.

---

## Current data concepts already in use

Based on the current exploration, the system works with concepts including:

- ordered `(observed_on, value)` history
- `reported_at`
- `observation_id`
- `attributes`
- cadence inference
- per-lookback applicability
- per-lookback trend snapshots
- canonical trend selection
- descriptor persistence
- reversal-event metadata when canonical direction changes
- API/UI-facing canonical and snapshot trend descriptors
- user-visible vs audit-only notification visibility modes
- trend change event idempotency fingerprints
- user subscription fan-out
- persisted in-app notification delivery records

The existing system also appears to use `observed_on + reported_at` ordering for some descriptor-resolution behavior.

---

## Current lookback catalog

The configured lookback catalog currently includes:

- `1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500, 1000`

Important notes:

- All catalog lookbacks are evaluated on each run.
- A lookback being “unused” in practice does **not** mean it is skipped by code.
- A lookback may be evaluated but marked **inapplicable** for a given series/run.
- Only **applicable** lookbacks produce snapshot outputs and participate in canonical selection.

***QUESTION: is the current selection of lookbacks (1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500, 1000) problematic? The goal is, for every observation, to be able to look back and say "what was the trend at this point?" And for the current trend to be treated as the canonical trend in the UI and for alerting purposes. I'm concerned by the breadth of the periods (1, 2, 3 being very small, 500, 1000 being very large), but also I do want to be able to label something as trending upward if it has happened recently and is significant.*** 

***ANSWER: Use the full configured lookback catalog for evidence generation and historical snapshotting, but do not treat all windows as equally eligible to become the canonical trend. The shortest windows (1, 2, 3) should be interpreted primarily as recent-movement or early-reversal signals and should only drive canonical direction when corroborated by nearby longer windows. Intermediate windows (4, 5, 10, 25, 50, 100) should be the primary basis for canonical trend selection, because they better balance responsiveness and stability. The longest windows (250, 500, 1000) should be retained as long-horizon context and regime evidence, informing interpretation and tie-breaking but not usually overriding stronger, consistent medium-horizon evidence about the current trend.***

---

## Current applicability behavior

For each catalog lookback, the system records an applicability result.

Known applicability states:

- `applicable`
- `inapplicable` with reason

Known inapplicability reasons include at least:

- insufficient history
- cadence/lookback not supported

From current notes, a lookback is inapplicable when at least one of these is true:

- `lookback_points >= len(observations)`  
  or equivalent insufficient-history condition
- lookback exceeds cadence-specific maximum supported depth

Current cadence-specific ceilings appear to be:

- daily: max lookback `1000`
- weekly: max lookback `500`
- monthly: max lookback `250`

Treat those values as current behavior, not necessarily desired future behavior.

---

## Current per-lookback analysis behavior

The current system uses a relatively simple rule-based approach per lookback.

Each applicable lookback may include or derive:

- relative change from value at `N` points ago to latest value
- direction: `up` or `down`
- strength: `mild` or `strong`
- trend label / outcome
- seasonality classification heuristic
- significance outcome

Thresholds:

- significant if absolute relative change `>= 0.05`
- strong if absolute relative change `>= 0.10`
- seasonality heuristic currently includes a monthly-series heuristic requiring at least `24` points

Known per-lookback outcome values include:

- `significant_trend`
- `no_significant_trend`

This should be treated as a descriptive simplification until confirmed in code. 

---

## Current canonical selection behavior

Canonical selection currently chooses a single current trend descriptor from the set of applicable lookback snapshots.

Important current behavior:

- only applicable lookbacks participate in canonical selection
- canonical selection currently favors **shorter lookbacks** (potentially problematic, see discussion above)
- current scoring has been described as:

`(1 / lookback) * strength_multiplier`

with at least:

- `mild = 1`
- `strong = 2`

Implication:

- very short windows are structurally advantaged (problematic, see discussion above)
- very large lookbacks can be applicable but rarely selected
- large windows tend to matter only when shorter windows are weak or non-significant

This is a major planning consideration because it shapes how “trend” is defined in practice in the current system.

---

## Exact canonical descriptor schema and enum contract

### Compute-layer source of truth

Source-of-truth computed canonical type:

`libs/trend_analysis/src/trend_analysis/models.py:70`  
`CanonicalTrendDescriptorResult`

Fields:

- `descriptor_state: Literal["available", "unavailable"]`
- `weighting_version: str`
- `trend_label: str | None`
- `direction: Literal["up", "down"] | None`
- `strength: Literal["mild", "strong"] | None`
- `selected_lookback_points: int | None`
- `reason_code: str | None`
- `weighting_trace: dict[str, object] | None`

### Pipeline persistence payload contract

Persistence contract used by pipeline:

`apps/pipeline/src/orchestration/resources/trend_repository.py:60`  
`CanonicalDescriptorInsert`

Fields include:

- `descriptor_state: Literal["available", "unavailable"]`
- `canonical_direction: Literal["up", "down"] | None`
- `canonical_trend_label`
- `canonical_strength`
- `selected_lookback_points`
- `weighting_version`
- `weighting_trace`
- `series_key`
- `observed_on`
- `observation_id`

### Database canonical descriptor schema

DB model:

`libs/db/src/db/models/trends.py:203`  
`TrendCanonicalDescriptor` (`trend_canonical_descriptors`)

Columns include:

- `descriptor_state` (required string)
- `canonical_trend_label` (nullable string)
- `canonical_direction` (nullable string)
- `canonical_strength` (nullable string)
- `selected_lookback_points` (nullable int)
- `weighting_version` (required string)
- `weighting_trace` (nullable JSONB)
- `observed_on`
- `observation_id`
- `data_series_id`
- `created_at`

Constraints include:

- `descriptor_state IN ('available', 'unavailable')`
- `canonical_direction IS NULL OR canonical_direction IN ('up', 'down')`
- `selected_lookback_points IS NULL OR selected_lookback_points > 0`
- `UNIQUE (data_series_id, observation_id)`

### Repository upsert mapping

Current repository mapping:

`apps/pipeline/src/orchestration/resources/postgres_trend_repository.py:379`

Maps:

- `canonical.descriptor_state -> descriptor_state`
- `canonical.trend_label -> canonical_trend_label`
- `canonical.direction -> canonical_direction`
- `canonical.strength -> canonical_strength`
- `canonical.selected_lookback_points -> selected_lookback_points`
- `canonical.weighting_version -> weighting_version`
- `canonical.weighting_trace -> weighting_trace::jsonb`

### Backend API contracts exposing canonical descriptor

#### Summary/list contract

`apps/backend/src/contract/query/dataset_search_query.py:17`  
`SummaryCanonicalTrendDescriptor`

Uses:

- `descriptor_state: Literal["available", "unavailable"]`
- `direction: Literal["up", "down"] | None`
- `selected_lookback_points: int | None` with `ge=1`
- `trend_label`, `strength`, `observed_on`, `reason_code` as nullable strings

#### Detail contract

`apps/backend/src/contract/query/dataset_detail_query.py:20`  
`CanonicalTrendDescriptor`

This is string-typed in places, but validation enforces that if `descriptor_state == "available"`, the payload must include:

- `trend_label`
- `direction`
- `strength`
- `selected_lookback_points`
- `observed_on`

### Practical enum contract that matters most

For current alert generation and downstream compatibility, the operationally important canonical descriptor values are:

- `descriptor_state: available | unavailable`
- `direction: up | down | null`
- `strength: mild | strong | null`

Important implication:

- there is currently **no explicit canonical `flat` direction enum**
- absence of usable direction is represented through the unavailable/null path, not through a third direction state

This is a central design constraint for any upgrade, and handling of flat direction will be necessary.

---

## Why the exact canonical schema matters

The canonical descriptor is a hard coupling point between:

1. trend computation,
2. persistence,
3. backend read contracts,
4. and alert generation.

The current system has strong assumptions baked into this contract:

- if descriptor is `available`, direction is expected to be `up` or `down`
- `selected_lookback_points` is expected for available descriptors
- alerting currently consumes only `up` / `down`
- DB constraints and API validation reinforce the two-direction model

Planning implication:

- any proposal that introduces a canonical `flat`, `mixed`, `uncertain`, or confidence-graded direction must explicitly account for:
  - compute-model changes,
  - persistence-schema changes,
  - DB constraint changes,
  - backend contract changes,
  - alerting semantics changes,
  - and historical compatibility behavior.

---

## Persisted and exposed trend outputs

The current system appears to persist or expose at least these categories of outputs:

### Persisted trend-analysis outputs

- lookback applicability rows
- lookback snapshot rows
- canonical descriptor rows
- reversal-event metadata when canonical direction flips

### API/UI-facing trend data

- dataset summary/detail canonical descriptor
- detail lookback snapshots
- observation-level as-of descriptor candidates
- descriptor resolution based on `observed_on + reported_at` ordering

These output contracts matter. Proposed upgrades should identify which of these can remain stable and which will need schema or semantic changes.

---

## Current alerting / notification pipeline

This system does not stop at computing a canonical trend. Canonical trend direction is also used to generate alert events and user-facing notifications.

### End-to-end path

Current conceptual path:

`trend reversal detected in canonical direction -> trend_change_event row -> conditional fan-out to subscribed users -> notification read/list/summary APIs`

### Where trend-to-alert conversion happens

Trend evaluation happens during ingest processing.

Current summary of flow:

1. `TrendRuntimeProcessor.process_series` computes lookback and canonical trend during ingest processing.
2. After `evaluate_multi_lookbacks(...)`, the pipeline extracts canonical direction from `evaluation.canonical_descriptor.direction` only when descriptor state is available.
3. If canonical descriptor state is unavailable, direction is treated as unavailable (`None`).
4. Lifecycle/run context determines visibility mode:
   - incremental processing -> `user_visible`
   - full historical reprocessing / backfill -> `audit_only`
5. Reversal detection occurs in `TrendNotificationService.process_canonical_transition`.
6. For a qualifying reversal, one event row is persisted idempotently.
7. Only `user_visible` events are fanned out to currently active subscribers.
8. Fan-out creates per-user notification rows for in-app delivery and read-state handling.
9. Backend notification APIs expose these records to clients.

### Exact notification coupling point

Critical bridge from canonical descriptor to alerting:

`apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py:141`

Current behavior summary:

- `current_direction = canonical.direction if canonical.descriptor_state == "available" else None`

That value is then consumed by:

`apps/pipeline/src/orchestration/jobs/trend_notification_service.py:39`

which gates to only:

- `{"up", "down"}`

This is the exact point where canonical descriptor semantics become notification semantics.

### Reversal detection gate

A trend change event is emitted only when all of the following are true:

- current canonical direction is `up` or `down`
- there is a prior canonical direction
- prior direction differs from current direction

Otherwise the pipeline records or returns non-event reasons such as:

- `direction_unavailable`
- `no_prior_direction`
- `direction_unchanged`

This means the current alerting semantics are specifically about **canonical directional reversal**, not generic “trend changed” behavior.

### Visibility mode semantics

Run context affects whether a reversal becomes user-visible.

Current behavior:

- incremental processing -> `user_visible`
- full historical reprocessing / backfill -> `audit_only`

This implies that planning changes to trend semantics must account for whether historical replay would generate large numbers of audit-only reversals, and whether the new method changes replay output substantially.

### Idempotent event persistence

For qualifying reversals, the system writes a single `trend_change_events` row using an idempotency fingerprint with components including:

- series
- date
- previous direction
- current direction
- context

Planning implication:

- any change to canonical-direction semantics or event keys may affect idempotency behavior, migration strategy, and duplicate suppression.

### User notification fan-out

For `user_visible` events only, the repository fans out to active subscribers.

Current subscription behavior includes:

- only subscribers with `unsubscribed_at IS NULL`
- only users subscribed before event emission

Fan-out inserts rows into `user_trend_notifications` with conflict protection equivalent to:

- `ON CONFLICT (event_id, user_id) DO NOTHING`

Planning implication:

- downstream fan-out assumes event identity is stable and meaningful.
- changing event semantics may require versioning or dual-writing strategy.

### Notification payload shape

Each persisted notification row stores fields including:

- destination path
- title
- body
- unread state
- channel = `in_app`
- delivery status = `delivered`

Planning implication:

- if trend semantics become richer, decide whether notification copy remains simple reversal text or gains new metadata such as confidence, break detection, or “post-break uptrend”.

### Backing schema

Migration `0015_trend_notifications` creates at least:

- `trend_change_events`
- `user_dataset_subscriptions`
- `user_trend_notifications`

with uniqueness, check, and index constraints.

Planning implication:

- schema changes touching event semantics should be evaluated against these existing constraints and read models.

### Backend read APIs

Notification APIs are exposed via `/api/notifications*` and backed by a trend notification service and persisted repository.

Planning implication:

- backend contract stability matters.
- if new event types or reasons are introduced, the API contract and contract tests may need revision.

### Existing test coverage that locks behavior

The following test areas exist and should be treated as behavioral constraints until intentionally changed:

- pipeline reversal / fan-out / audit-only behavior
- pipeline idempotency semantics
- DB repository fan-out / idempotency / read-state paths
- backend contract / endpoint shape / auth behavior

Planning implication:

- proposed trend-method changes need a test migration plan, not just a code migration plan.

---

## Why the alerting path matters for this redesign

The trend-analysis subsystem is not purely descriptive. It is an event source.

That creates additional constraints:

1. **Canonical direction is operationally significant**  
   It is used to decide whether an alert event exists.

2. **Instability in canonical direction has user impact**  
   A noisier or more sensitive method can create alert churn.

3. **Historical equivalence matters**  
   A new method may change event history under replay or reprocessing.

4. **Idempotency semantics matter**  
   Event identity is tied to trend semantics.

5. **A better method is not enough by itself**  
   It must also be stable enough to support notification behavior.

Because of this, the redesign should evaluate not only “is the trend estimate better?” but also “does it create acceptable reversal behavior for notifications?”

---

## Current strengths of the existing design

The architecture already has useful properties:

1. **Multi-horizon evaluation**  
   It does not rely on a single fixed window.

2. **Applicability gating**  
   It explicitly records which windows can and cannot be used.

3. **Snapshot + canonical separation**  
   It distinguishes underlying per-lookback evidence from the final chosen description.

4. **Persistence and explainability hooks**  
   The system already stores intermediate and canonical outputs, which should make migration and A/B comparison easier.

5. **Operational simplicity**  
   The current rule-based model is easy to compute and explain.

6. **Operational alerting integration already exists**  
   Canonical direction already plugs into a full event and notification pipeline.

These strengths should be preserved where feasible.

---

## Current weaknesses / likely failure modes

The present method appears vulnerable to several issues:

### 1. Endpoint sensitivity

Using percent change from `N` points ago to the latest value makes the signal highly sensitive to:

- a noisy final observation
- an anomalous starting point within the window
- a one-time spike or dip

### 2. Weak robustness to outliers

A single extreme point can materially alter direction and strength labeling.

### 3. Weak handling of noisy monotone trends

A genuine upward or downward tendency can be masked if endpoints are unrepresentative.

### 4. Weak handling of seasonality

A heuristic seasonality flag is less reliable than explicit decomposition or seasonal adjustment.

### 5. Bias toward short horizons

The current canonical score strongly prefers short lookbacks, potentially overreacting to short-term noise.

### 6. Limited notion of significance

Fixed thresholds on percent change are easy to understand but are not the same as statistical evidence of a monotonic trend.

### 7. Poor regime-shift representation

A series that was flat for a long time and then recently jumped may be better described as a structural break plus a new regime, rather than one monotonic lookback trend.

### 8. Potential notification churn

Because canonical directional reversals trigger events, a brittle canonical selector can create:

- false reversals
- unstable notification behavior
- higher sensitivity to local noise than users likely want

### 9. Canonical enum rigidity

The current canonical contract is tightly constrained to:

- descriptor state `available | unavailable`
- direction `up | down | null`

This makes the current system operationally simple, but narrows the space of upgrade options unless compatibility layers are introduced.

---

## Desired direction of change

We want to keep the broad shape of the current system, but improve the statistical core.

The current working idea is:

- keep cadence and applicability stages,
- keep multi-lookback evaluation,
- keep per-lookback snapshots,
- keep canonical resolution,
- upgrade how per-lookback trend evidence is computed,
- possibly upgrade canonical arbitration,
- optionally add explanatory metadata for regime shifts or seasonal adjustment,
- preserve or carefully version the operational semantics used for reversal alerts.

---

## Recommended upgrade components for the next version

The next version of the trend-analysis system should preserve the current multi-lookback architecture, but replace the weakest parts of the current signal-generation logic with more robust methods. The recommendations below are intended to work together as a staged upgrade path, not as mutually exclusive alternatives.

### Recommendation 1: use robust slope-based scoring for each applicable lookback

Replace endpoint relative change as the primary per-lookback trend signal with a more robust slope estimate computed over the full lookback window.

Recommended method:

- use a robust slope estimator such as **Theil-Sen** as the primary trend estimate for each applicable lookback
- retain ordinary least squares, if useful, only as a diagnostic or comparison metric, not as the primary decision signal
- normalize slope into a comparable per-period or percent-per-period representation where needed
- optionally compute supporting monotonic-trend evidence such as Kendall tau or a Mann-Kendall significance measure

This should become the default basis for per-lookback trend classification.

Expected mapping to existing concepts:

- `direction` -> sign of robust slope
- `strength` -> bucketed normalized slope magnitude
- `trend significance / evidence` -> statistical or rank-based support threshold
- lookback snapshot row remains the core output unit

Why this is recommended:

- it remains compatible with the current per-lookback evaluation model
- it is less sensitive to noisy endpoints and isolated outliers
- it should produce more stable canonical direction outcomes than endpoint-delta logic
- it is the lowest-disruption improvement with the highest likely benefit

Alerting implication:

- a more robust per-lookback signal should reduce spurious canonical reversals and therefore reduce false or noisy reversal notifications

---

### Recommendation 2: add preprocessing through smoothing before per-lookback scoring

The system should support preprocessing of the analysis series before per-lookback scoring when doing so improves stability and interpretability.

Recommended methods:

- use **EWMA** or another lightweight smoother for noisy series where a simple stabilizing pass is sufficient
- allow robust rolling or median-based smoothing where appropriate
- use **STL**-based preprocessing when cadence is regular and history is sufficient to support decomposition

This preprocessing step should be introduced as an explicit stage in the pipeline, prior to per-lookback trend scoring.

Recommended behavior:

- smoothing should not necessarily be universal
- smoothing should be applied according to cadence, history depth, and data quality characteristics
- raw and preprocessed values should remain distinguishable for debugging, evaluation, and traceability

Why this is recommended:

- it preserves the current architecture
- it improves signal stability without forcing a redesign of snapshot or canonical selection logic
- it creates a clearer foundation for stable canonical selection and alert generation

Alerting implication:

- smoothing should improve reversal stability, but it must be calibrated to avoid excessive lag in reversal detection

---

### Recommendation 3: replace heuristic seasonality handling with explicit seasonal adjustment where supported

The current seasonal heuristic should be replaced, where feasible, with explicit seasonal adjustment or decomposition.

Recommended methods:

- use **STL** or comparable decomposition for regular cadences with sufficient history
- compute trend on the seasonally adjusted series or on the extracted trend component
- only enable seasonal adjustment when cadence regularity and observation history make the decomposition reliable

Recommended behavior:

- seasonal adjustment should be a supported preprocessing mode, not a separate competing trend system
- where seasonal adjustment is not supported or reliable, the system should fall back to non-seasonally-adjusted scoring and record that decision explicitly

Why this is recommended:

- it gives a more defensible separation between trend and recurring seasonal fluctuation
- it fits naturally into the current architecture as a preprocessing refinement
- it should improve both descriptive accuracy and stability of canonical trend selection for seasonal series

Alerting implication:

- explicit seasonal adjustment may shift canonical reversal timing relative to the current system, so historical replay and notification-delta analysis should be part of rollout planning

---

### Recommendation 4: add change-point detection as companion metadata, not as the primary trend classifier

The upgraded system should support change-point or regime-shift detection as a secondary explanatory layer.

Recommended use cases:

- identify recent structural breaks
- annotate canonical trend as a recent reversal, post-break uptrend, post-break downtrend, or similar explanatory state
- improve interpretability when long-horizon and short-horizon evidence conflict
- provide better context for reversal events without replacing the core canonical-direction model

Recommended behavior:

- change-point detection should be additive
- it should not replace the canonical trend descriptor in the first phase of the upgrade
- it should initially be used for metadata, interpretation, debugging, and potential future alert refinement

Why this is recommended:

- it improves explanation without forcing major architectural change
- it helps distinguish gradual monotonic movement from genuine regime shifts
- it provides a path toward richer future alert semantics while preserving current operational assumptions

Alerting implication:

- in the initial rollout, change-point detection should not replace the current reversal-event model
- it may later support improved notification copy or additional event types, but only after canonical-direction stability is validated

---

## How these recommendations should be applied together

These recommendations should be treated as a staged upgrade path:

### Phase 1

Adopt robust slope-based per-lookback scoring as the new default trend signal.

### Phase 2

Introduce smoothing and explicit seasonal adjustment where cadence and history support them.

### Phase 3

Add change-point detection as companion metadata to improve interpretation, canonical selection quality, and future alerting flexibility.

This sequence is recommended because it improves the core trend signal first, preserves the current architecture, and reduces implementation risk while leaving room for later refinement.

---

## Architectural principle for planning

The planning work should assume this target shape unless a strong reason emerges to change it:

1. **cadence / applicability**
2. **optional preprocessing**
3. **per-lookback evidence generation**
4. **canonical arbitration**
5. **persistence + API/UI outputs**
6. **canonical-transition eventing and notification fan-out**

The planning work should explicitly call out whether each proposed method:

- preserves this structure,
- slightly modifies it,
- or requires major redesign.

---

## Questions the planning work should answer

### Canonical contract strategy

Should the upgrade:

1. preserve the canonical descriptor contract exactly,
2. preserve it externally but enrich it internally,
3. or version it and introduce new enums / semantics?

This is one of the highest-priority planning questions.

### Data-contract impact

What new fields, if any, would be needed in:

- lookback applicability rows
- lookback snapshot rows
- canonical descriptor rows
- reversal-event metadata
- trend change event rows
- user notifications
- API/UI-facing trend payloads
- notification API payloads

### Canonical arbitration redesign

How should canonical selection change if per-lookback evidence becomes slope-based rather than threshold-percent-change-based?

Specific subquestions:

- should short lookbacks still be favored?
- if yes, how much?
- how should agreement across neighboring lookbacks matter?
- how should significance/effect size/recency trade off?
- should canonical selection optimize for descriptive accuracy, alert stability, or some explicit combination?

### Alert semantics and reversal stability

How should the system preserve or revise the current rule:

`prior canonical direction != current canonical direction -> reversal event`

Specific subquestions:

- should reversal semantics remain exactly directional?
- should `flat` / `no meaningful trend` participate explicitly?
- if no explicit `flat` is introduced, is `unavailable` the right representation for weak/no-trend cases?
- should there be hysteresis or debounce logic before firing a reversal?
- should event emission use the exact same canonical direction as API/UI display, or a stabilized derivative of it?
- how should replay/backfill behavior differ from incremental behavior under the new method?

### Seasonality strategy

Under what conditions should the system:

- do nothing,
- smooth only,
- decompose seasonality,
- or reject trend classification as unreliable?

### Irregular cadence and missingness

How should robust trend estimation behave when:

- cadence is irregular,
- gaps are large,
- observations are sparse,
- or values are missing?

### Backward compatibility

Which existing output semantics can be preserved, and which should be versioned or renamed?

This includes:

- trend snapshot semantics
- canonical descriptor semantics
- reversal-event semantics
- notification payload semantics
- audit-only vs user-visible run behavior
