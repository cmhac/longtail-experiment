# Data Model: Per-Source Asset Cadence

## Entities

### 1. Source Asset

- Purpose: Represents an ingest source with independent scheduling ownership.
- Core Attributes:
- source_key: Stable source identifier.
- activation_state: Active, paused, or disabled for scheduled execution.
- run_modes: Supported trigger modes (scheduled, on-demand).
- visibility_state: Exposed in operator catalog views.
- Relationships:
- One Source Asset has one active schedule definition.
- One Source Asset can produce many source-level run outcomes.

### 2. Source Schedule

- Purpose: Defines cadence and trigger ownership for one source asset.
- Core Attributes:
- schedule_key: Stable schedule identifier linked to source asset.
- source_key: Owning source asset.
- cadence: Human-readable cadence intent for operator visibility.
- schedule_state: Enabled or paused.
- trigger_origin_label: Label used in run attribution.
- Relationships:
- One Source Schedule belongs to one Source Asset.
- One Source Schedule creates many scheduled run events over time.

### 3. Scheduled Run Record

- Purpose: Captures a scheduled execution event and its source-level results.
- Core Attributes:
- run_id: Unique run identifier.
- source_key: Source executed by this schedule event.
- trigger_type: Scheduled or on-demand.
- trigger_origin: Schedule or operator token used to initiate run.
- started_at / completed_at: Execution window.
- outcome_state: Aggregate run status.
- source_results: Source-level accepted, quarantined, failed, and reason fields.
- Relationships:
- One Scheduled Run Record maps to one source schedule trigger context.
- Many run records belong to one source over time.

### 4. Legacy Scheduling Artifact Context

- Purpose: Describes how to interpret pre-cutover schedule policy and eligibility data after migration.
- Core Attributes:
- artifact_type: Legacy schedule-policy or eligibility snapshot.
- lifecycle_state: Historical-only, non-authoritative.
- interpretation_note: Operator-facing explanation of post-cutover meaning.
- retention_window: Duration for keeping legacy records queryable.
- Relationships:
- Can reference historical run records for audit.
- Has no authority over current cadence decisions.

## Validation Rules

- Every active Source Asset must have exactly one associated active Source Schedule.
- Scheduled run attribution must include source_key and trigger_origin.
- Source assets in paused or disabled state must not produce scheduled run events.
- Source assets may still support on-demand runs when scheduled state is paused.
- Legacy scheduling artifacts must not influence post-cutover due decisions.

## State Transitions

### Source Asset Activation State

- active -> paused: schedule exists but does not trigger automatic runs.
- paused -> active: schedule resumes cadence-based triggers.
- active/paused -> disabled: source excluded from scheduled execution.

### Source Schedule State

- enabled -> paused: cadence temporarily suspended.
- paused -> enabled: cadence resumes from schedule authority.

### Run Trigger Lifecycle

- scheduled_request_created -> run_started -> run_completed
- on_demand_request_created -> run_started -> run_completed
- run_completed includes source-level outcomes and trigger attribution.
