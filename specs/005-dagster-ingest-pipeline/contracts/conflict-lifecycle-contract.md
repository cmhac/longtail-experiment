# Contract: Duplicate Drift and Conflict Lifecycle

## Purpose

Define deterministic handling of duplicate records and conflict persistence behavior for same series and reference period inputs.

## Version

- Contract: conflict-lifecycle
- Version: v1
- Status: Draft for implementation planning

## Drift Classification

For an incoming record matching an existing canonical series-period key:

- `exact_duplicate`:
  - incoming value and semantics match existing stored version
  - emit `duplicate_no_op`
  - do not write a new canonical observation version
- `conflicting_duplicate`:
  - incoming value or semantics differ from stored version
  - emit `conflict`
  - persist a ConflictRecord with references to both record contexts

## Conflict Record Contract

ConflictRecord MUST include:

- conflictId
- runId
- sourceKey
- seriesKey
- referencePeriodKey
- existingObservationRef
- incomingRecordRef
- conflictType
- conflictState
- createdAt

## Conflict State Contract

- Allowed states: open, acknowledged, resolved
- State transitions:
  - open -> acknowledged
  - acknowledged -> resolved
- Resolved records MUST include resolvedAt metadata.

## Queryability Requirements

- Conflict records MUST be queryable by:
  - sourceKey
  - seriesKey
  - referencePeriodKey
  - conflictState
  - runId
- Ingestion run summaries MUST include conflict counts.

## Validation Rules

- Existing and incoming record references MUST be non-empty.
- conflictType MUST be from a controlled taxonomy.
- conflict outcomes MUST never be silently downgraded to no-op or accepted.

## Compatibility and Evolution

- Additional conflict classification values are additive.
- Changes to required conflict fields or state semantics require version bump and migration guidance.
