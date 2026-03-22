# Data Model: Parallel Source Scheduling and Bounded Concurrency

## Entity: SourceSchedulePolicy

- Description: Declares one source's cadence and eligibility controls.
- Fields:
  - sourceKey: stable source identity key
  - cadenceType: hourly, daily, weekly, monthly, custom_interval
  - cadenceValue: optional numeric interval value for custom cadence
  - timezone: policy evaluation timezone reference
  - isActive: eligibility switch for scheduler participation
  - lastSuccessfulAt: timestamp of last successful source run
  - nextEligibleAt: computed timestamp for next due evaluation
  - priorityClass: scheduling priority bucket for backlog handling
- Validation rules:
  - sourceKey MUST map to an active registered source workflow.
  - cadenceType MUST be one of allowed cadence values.
  - cadenceValue MUST be present and positive when cadenceType is custom_interval.
  - nextEligibleAt MUST be >= lastSuccessfulAt when both are present.
- Relationships:
  - SourceSchedulePolicy has many SourceEligibilitySnapshot records.

## Entity: RunConcurrencyPolicy

- Description: Defines bounded parallel launch behavior for one orchestration run.
- Fields:
  - runId: parent run identity
  - maxActiveSources: configured concurrency ceiling
  - activeSourceCount: current active source executions
  - queuedDueCount: number of due sources waiting for slots
  - launchOrderingKey: deterministic ordering strategy identifier
- Validation rules:
  - maxActiveSources MUST be >= 1.
  - activeSourceCount MUST be <= maxActiveSources.
  - queuedDueCount MUST be >= 0.
- Relationships:
  - RunConcurrencyPolicy belongs to one IngestionRun.

## Entity: SourceEligibilitySnapshot

- Description: Per-source due-state decision captured at run planning time.
- Fields:
  - snapshotId: unique eligibility snapshot identifier
  - runId: parent run identity
  - sourceKey: source identity
  - eligibilityState: due, not_due, skipped_inactive, skipped_invalid_policy
  - evaluatedAt: due-state evaluation timestamp
  - dueAt: timestamp when source became eligible
  - reasonCode: normalized code explaining inclusion or exclusion
  - selectedForExecution: true when source is planned for launch
- Validation rules:
  - one snapshot per sourceKey per runId.
  - selectedForExecution MUST be false when eligibilityState is not_due or skipped states.
- Relationships:
  - SourceEligibilitySnapshot belongs to one IngestionRun.
  - SourceEligibilitySnapshot references one SourceSchedulePolicy by sourceKey.

## Entity: SourceExecutionSlot

- Description: Captures source launch and completion lifecycle under bounded concurrency.
- Fields:
  - slotEventId: unique slot lifecycle event identifier
  - runId: parent run identity
  - sourceKey: source identity
  - slotState: queued, active, completed, failed, cancelled
  - queuedAt: queued timestamp
  - startedAt: active execution start timestamp
  - finishedAt: completion timestamp
  - workerToken: execution allocation token
- Validation rules:
  - slotState active requires startedAt.
  - finishedAt MUST be >= startedAt when both are present.
  - one active slot per sourceKey across overlapping runs.
- Relationships:
  - SourceExecutionSlot belongs to one IngestionRun.

## Entity: SourceRunOutcome (Extended)

- Description: Source terminal outcome with explicit non-execution classifications.
- Fields:
  - sourceOutcomeId: unique source outcome identifier
  - runId: parent run identity
  - sourceKey: source identity
  - state: success, partial_success, failure, deferred, not_due
  - acceptedCount: accepted record count
  - quarantinedCount: quarantined record count
  - failedCount: failed record count
  - duplicateNoOpCount: no-op duplicate count
  - conflictCount: conflict count
  - outcomeReasonCode: optional reason for deferred/not_due
  - message: optional operator-readable summary
- Validation rules:
  - state not_due requires acceptedCount, failedCount, and conflictCount to be zero.
  - state deferred requires outcomeReasonCode.
- Relationships:
  - SourceRunOutcome belongs to one IngestionRun.

## Entity: IngestionRun (Extended)

- Description: Aggregate orchestration execution summary.
- Fields:
  - runId: unique run identifier
  - triggerType: scheduled or on_demand
  - startedAt: run start timestamp
  - completedAt: run completion timestamp
  - outcomeState: success, partial_success, failure
  - dueSourceCount: number of due sources evaluated for potential execution
  - executedSourceCount: number of sources launched and completed/failed
  - deferredSourceCount: due sources not executed in current run by policy
  - notDueSourceCount: evaluated sources excluded for not-due policy
  - failedSourceCount: number of sources with terminal failure
- Validation rules:
  - completedAt MUST be >= startedAt.
  - executedSourceCount + deferredSourceCount MUST be <= dueSourceCount.
- Relationships:
  - IngestionRun has many SourceEligibilitySnapshot records.
  - IngestionRun has many SourceRunOutcome records.

## State Transition Summary

- SourceEligibilitySnapshot:
  - evaluated -> due
  - evaluated -> not_due
  - evaluated -> skipped_inactive
  - evaluated -> skipped_invalid_policy
- SourceExecutionSlot:
  - queued -> active -> completed
  - queued -> active -> failed
  - queued -> cancelled
- SourceRunOutcome:
  - pending -> success
  - pending -> partial_success
  - pending -> failure
  - pending -> deferred
  - pending -> not_due

## Integrity Constraints

- At most one active execution per source key across overlapping runs.
- Bounded concurrency MUST cap simultaneous active source slots per run.
- Scheduled runs MUST only launch sources marked due and selectedForExecution=true.
- On-demand subset execution MUST only include requested source keys that are valid registrations.
- Deterministic ordering key MUST produce stable launch order for equivalent eligibility sets.
