# Data Model: Dagster-Orchestrated Time-Series Ingestion

## Entity: IngestionWorkflowDefinition

- Description: A registered source-specific workflow executed by the orchestration layer.
- Fields:
  - workflowId: unique workflow identifier
  - sourceKey: stable source identity key
  - owner: owning team or maintainer reference
  - triggerModes: supported trigger modes (scheduled, on-demand)
  - status: active, paused, retired
  - registrationVersion: workflow registration revision
- Validation rules:
  - sourceKey MUST be unique among active workflows.
  - triggerModes MUST include at least one mode.
  - retired workflows MUST NOT accept new triggers.
- Relationships:
  - IngestionWorkflowDefinition has many IngestionRun records.

## Entity: IngestionRun

- Description: One orchestration execution instance with aggregate lifecycle and status.
- Fields:
  - runId: unique run identifier
  - triggerType: scheduled or on-demand
  - startedAt: run start timestamp
  - completedAt: run completion timestamp
  - lifecycleState: queued, running, completed, failed
  - outcomeState: success, partial_success, failure
  - acceptedCount: accepted record count
  - quarantinedCount: quarantined record count
  - failedCount: failed record count
  - duplicateNoOpCount: exact-duplicate no-op count
  - conflictCount: non-matching duplicate conflict count
- Validation rules:
  - completedAt MUST be >= startedAt when present.
  - outcomeState partial_success MUST require at least one success and at least one failure outcome at source level.
- Relationships:
  - IngestionRun has many SourceRunOutcome records.

## Entity: SourceRunOutcome

- Description: Source-scoped outcome within an ingestion run.
- Fields:
  - sourceOutcomeId: unique source outcome identifier
  - runId: parent run reference
  - sourceKey: source identity
  - state: success, partial_success, failure
  - acceptedCount: accepted records for source
  - quarantinedCount: quarantined records for source
  - failedCount: failed records for source
  - duplicateNoOpCount: no-op duplicates for source
  - conflictCount: conflicts for source
  - message: short summary for operators
- Validation rules:
  - sourceKey MUST reference a registered active workflow at run start.
  - state MUST align with record counts.
- Relationships:
  - SourceRunOutcome belongs to one IngestionRun.

## Entity: SourceRunLock

- Description: Concurrency control state for a source workflow.
- Fields:
  - sourceKey: source identity (primary key)
  - activeRunId: optional active run reference
  - queuedTriggerToken: optional deduplicated pending trigger marker
  - lockUpdatedAt: last lock state transition timestamp
- Validation rules:
  - At most one activeRunId per sourceKey.
  - At most one queuedTriggerToken per sourceKey.
- State transitions:
  - idle -> active
  - active -> active_with_queued
  - active_with_queued -> active (after queued promotion)
  - active -> idle

## Entity: IngestionRecordOutcome

- Description: Per-record ingest decision captured for audit and metrics.
- Fields:
  - recordOutcomeId: unique identifier
  - runId: parent run reference
  - sourceKey: source identity
  - seriesKey: canonical series identifier
  - referencePeriodKey: canonical period key
  - status: accepted, quarantined, failed, duplicate_no_op, conflict
  - reasonCode: normalized reason classification
  - reasonDetail: optional human-readable detail
  - observedAt: decision timestamp
- Validation rules:
  - status MUST map to an allowed reasonCode set.
  - duplicate_no_op and conflict MUST include referencePeriodKey.
- Relationships:
  - IngestionRecordOutcome belongs to one IngestionRun.

## Entity: ConflictRecord

- Description: Persisted conflict linking incompatible records for the same series and period.
- Fields:
  - conflictId: unique conflict identifier
  - runId: ingest run reference
  - sourceKey: source identity
  - seriesKey: canonical series identifier
  - referencePeriodKey: canonical period key
  - existingObservationRef: existing stored record reference
  - incomingRecordRef: incoming conflicting record reference
  - conflictType: value_mismatch, semantics_mismatch, duplicate_key_collision
  - conflictState: open, acknowledged, resolved
  - createdAt: conflict creation timestamp
  - resolvedAt: optional resolution timestamp
- Validation rules:
  - existingObservationRef and incomingRecordRef MUST both be present.
  - conflictState resolved MUST include resolvedAt.
- Relationships:
  - ConflictRecord belongs to one IngestionRun.
  - ConflictRecord links to canonical observations through record references.

## Entity: CanonicalObservationVersion (Existing)

- Description: Persisted canonical observation version from the shared contract model.
- Relevance in this feature:
  - Serves as the comparison baseline for duplicate drift checks.
  - Receives accepted writes from source workflows.
  - Participates in revision lineage and conflict association.

## State Transition Summary

- IngestionRun:
  - queued -> running -> completed
  - queued -> running -> failed
- SourceRunOutcome:
  - pending -> success
  - pending -> partial_success
  - pending -> failure
- ConflictRecord:
  - open -> acknowledged -> resolved

## Integrity Constraints

- Duplicate drift check MUST compare incoming record against current canonical observation for same series and period.
- Exact match MUST emit `duplicate_no_op` and MUST NOT create a new observation version.
- Non-matching duplicate MUST create `conflict` outcome and a ConflictRecord.
- Concurrency lock MUST enforce one active and one queued run per source.
