# Schema Compatibility Analysis: 014-Read-Only FastAPI API

**Date**: 2026-03-23
**Scope**: Compare the existing PostgreSQL 16 runtime schema (migrations 0001–0007 in `libs/db/alembic/versions/`) against the requirements in `spec.md`, `data-model.md`, and `contracts/phase1-api-contract.md` for feature 014.

---

## Summary

All four runtime tables required by Phase 1 (`ingestion_runs`, `source_run_outcomes`, `source_eligibility_snapshots`, `conflict_records`) exist in the current schema. All required columns are present. No new tables or columns are needed for Phase 1 functionality.

However, **two categories of incompatibility** were found that require correction before implementation can begin:

1. **Missing query-support indexes** — `conflict_records` has no indexes on any of the five filter columns used by `GET /api/conflicts`. A new Alembic migration (0008) is required.

2. **Enum value mismatches** — The spec's "stable value sets" for `source_run_outcomes.state` and `source_eligibility_snapshots.eligibility_state` were written with speculative names that do not match the actual string literals persisted by the pipeline. The spec and contract documents must be corrected to reflect actual DB values.

---

## Table Coverage Checklist

| API Endpoint | Table | All Required Columns Present? |
| ------------ | ----- | ----------------------------- |
| `GET /health` | (DB probe, no table) | ✅ |
| `GET /api/runs` | `ingestion_runs` | ✅ |
| `GET /api/runs/{run_id}` | `ingestion_runs` | ✅ |
| `GET /api/runs/{run_id}/outcomes` | `source_run_outcomes` | ✅ |
| `GET /api/runs/{run_id}/eligibility` | `source_eligibility_snapshots` | ✅ |
| `GET /api/conflicts` | `conflict_records` | ✅ |

---

## Incompatibility 1: Missing DB Indexes (Requires Migration 0008)

### Finding

`GET /api/conflicts` must support filtering by five optional parameters: `run_id`, `source_key`, `series_key`, `reference_period_key`, and `conflict_state`. PostgreSQL does **not** automatically create indexes for foreign key columns. The `conflict_records` table has only:

- A primary key index on `id` (UUID)
- A unique index on `conflict_id`

No indexes exist on any filter column. Every filtered or unfiltered scan of `conflict_records` will be a full sequential scan.

`GET /api/runs` orders by `started_at DESC`. The `ingestion_runs` table has no index on `started_at`. With a large number of runs, sorting without an index forces a full table sort on every request.

### Evidence

Inspected all migration files 0001–0007. The `conflict_records` table is created in `0002_ingestion_runtime_and_conflicts.py`:

```python
op.create_table(
    "conflict_records",
    sa.Column("id", sa.UUID(), ...),
    sa.Column("conflict_id", sa.String(length=64), ...),
    sa.Column("run_id", sa.String(length=64), ...),     # FK — no index
    sa.Column("source_key", sa.String(length=255), ...), # no index
    sa.Column("series_key", sa.String(length=255), ...), # no index
    sa.Column("reference_period_key", sa.String(length=64), ...), # no index
    sa.Column("conflict_state", sa.String(length=32), ...), # no index
    ...
    sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.run_id"]),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("conflict_id"),  # creates index on conflict_id only
)
```

### Required Fix

**New Alembic migration `0008_query_support_indexes`** must be created before implementing the API. It should add:

| Index Name | Table | Column(s) | Rationale |
| ---------- | ----- | --------- | --------- |
| `ix_conflict_records_run_id` | `conflict_records` | `run_id` | `GET /api/conflicts?run_id=X` |
| `ix_conflict_records_source_key` | `conflict_records` | `source_key` | `GET /api/conflicts?source_key=X` |
| `ix_conflict_records_conflict_state` | `conflict_records` | `conflict_state` | `GET /api/conflicts?conflict_state=X` |
| `ix_conflict_records_series_key` | `conflict_records` | `series_key` | `GET /api/conflicts?series_key=X` |
| `ix_conflict_records_reference_period_key` | `conflict_records` | `reference_period_key` | `GET /api/conflicts?reference_period_key=X` |
| `ix_ingestion_runs_started_at` | `ingestion_runs` | `started_at` | `GET /api/runs ORDER BY started_at DESC` |

**Note**: `source_run_outcomes` and `source_eligibility_snapshots` are acceptable as-is. Both have composite unique constraints on `(run_id, source_key)` that create a B-tree index with `run_id` as the leading column, allowing efficient prefix lookups for `WHERE run_id = :run_id` queries used by the outcomes and eligibility endpoints.

### Impact If Not Fixed

Without these indexes Phase 1 will still be functionally correct but SC-001 ("all endpoints respond within 500 ms for typical local development data volumes") may not be satisfied under modest data volume, and the conflict endpoint will degrade linearly with data growth.

---

## Incompatibility 2: Enum Value Mismatches (Requires Spec/Contract Corrections)

### Finding A: `source_run_outcomes.state`

The spec (`data-model.md`, `contracts/phase1-api-contract.md`) defines a "stable value set" for `SourceRunOutcomeResponse.state` as:

> `succeeded`, `failed`, `not_due`, `deferred`, `conflict`

The pipeline **actually writes** the following values to `source_run_outcomes.state` (confirmed from `apps/pipeline/src/orchestration/jobs/workflow_result.py` and `postgres_run_repository.py`):

| Written to DB | Spec says | Match? |
| ------------- | --------- | ------ |
| `success` | `succeeded` | ❌ |
| `partial_success` | (no equivalent) | ❌ |
| `failure` | `failed` | ❌ |
| `not_due` | `not_due` | ✅ |
| `deferred` | `deferred` | ✅ |
| `conflict` | `conflict` | ✅ |

Source: `SourceWorkflowResult.status` Literal in `workflow_result.py`:
```python
status: Literal["success", "partial_success", "failure", "deferred", "not_due"]
```

The repository maps `source_result["status"]` directly to `source_run_outcomes.state` without any translation.

**Additionally**: `partial_success` has no equivalent in the spec's value set. This is a source-level outcome that occurs when a source produces some accepted observations but also some failures. Omitting it from the contract would cause the API to silently serve `"partial_success"` values that clients cannot handle.

### Finding B: `source_eligibility_snapshots.eligibility_state`

The spec defines the stable value set for `SourceEligibilityResponse.eligibility_state` as:

> `eligible`, `not_due`, `skipped`

The pipeline actually writes (from `apps/pipeline/src/orchestration/jobs/due_source_selector.py`):

| Written to DB | Spec says | Match? |
| ------------- | --------- | ------ |
| `due` | `eligible` | ❌ |
| `not_due` | `not_due` | ✅ |
| `skipped_inactive` | `skipped` | ❌ |
| `skipped_invalid_policy` | `skipped` | ❌ |

The pipeline distinguishes between two skip reasons (`skipped_inactive` = source is marked inactive, `skipped_invalid_policy` = source has a malformed schedule policy). The spec collapses both to a single `"skipped"` value, which would lose diagnostic information.

### Finding C: `ingestion_runs.outcome_state`

The spec's example values for `IngestionRunResponse.outcome_state` show `"succeeded"`, `"failed"`, `"partial"`. The pipeline writes `"success"`, `"partial_success"`, `"failure"` (from `run_outcome_service.py`). Since the data-model labels these as `(e.g., ...)` examples rather than a closed enumeration, the mismatch is less severe. Still, the contract document uses these examples in JSON response samples, so they must be corrected.

### Required Fix

**Correct `data-model.md` and `contracts/phase1-api-contract.md`** to use the actual values persisted by the pipeline. Do NOT change the pipeline code — the pipeline values are the authoritative source since they define what is already in the DB.

Corrected value sets:

**`source_run_outcomes.state`** (was wrong, now corrected):

| Value | Meaning |
| ----- | ------- |
| `success` | Source executed to completion with all records accepted |
| `partial_success` | Source executed but produced some failures alongside successes |
| `failure` | Source encountered a terminal error |
| `not_due` | Source was not due for execution this run |
| `deferred` | Source execution was deferred for retry |
| `conflict` | Source produced one or more conflict records |

**`source_eligibility_snapshots.eligibility_state`** (was wrong, now corrected):

| Value | Meaning |
| ----- | ------- |
| `due` | Source was evaluated as due and selected for execution |
| `not_due` | Source cadence not yet satisfied |
| `skipped_inactive` | Source is marked inactive; skipped without evaluation |
| `skipped_invalid_policy` | Source schedule policy is malformed; skipped with error |

**`ingestion_runs.outcome_state`** (example correction only):

| Value | Meaning |
| ----- | ------- |
| `success` | All executed sources completed successfully |
| `partial_success` | Some sources succeeded and some failed |
| `failure` | All executed sources failed (or only failures occurred) |

---

## No-Issue Checklist (Confirmed Compatible)

The following were inspected and confirmed compatible with no changes required:

| Item | Status |
| ---- | ------ |
| `ingestion_runs` table and all 18 columns (including all counter fields added in migrations 0003 and 0005) | ✅ All present |
| `source_run_outcomes` table and all 11 columns including `outcome_reason_code` (added migration 0003) | ✅ All present |
| `source_eligibility_snapshots` table and all columns including `lifecycle_state` (added migration 0005) | ✅ All present; `lifecycle_state` not exposed in API response — no action needed |
| `conflict_records` table and all 12 columns | ✅ All present |
| `run_id` is a `String(64)` field on `ingestion_runs` used as the path parameter `{run_id}` | ✅ String path param; any string accepted; returns 404 if not found |
| FK from `source_run_outcomes.run_id` → `ingestion_runs.run_id` | ✅ Consistent with 404-before-child-resources pattern |
| FK from `source_eligibility_snapshots.run_id` → `ingestion_runs.run_id` | ✅ Same |
| FK from `conflict_records.run_id` → `ingestion_runs.run_id` | ✅ Same |
| `conflict_records.conflict_state` value set — pipeline only writes `"open"`; spec expects `open/resolved/suppressed` | ✅ No issue — API can filter by all values; empty result is valid |
| Composite unique index `uq_outcome_run_source` on `(run_id, source_key)` in `source_run_outcomes` | ✅ Run-id prefix scan efficient for outcomes endpoint |
| Composite unique index `uq_eligibility_run_source` on `(run_id, source_key)` in `source_eligibility_snapshots` | ✅ Run-id prefix scan efficient for eligibility endpoint |
| `UUID(as_uuid=True)` PK type on all tables vs. String run identifiers (`run_id`, `conflict_id`) | ✅ UUID PKs are internal; API uses string identifiers only |
| `DateTime(timezone=True)` on all timestamp columns — serializes correctly to ISO-8601 UTC | ✅ No conversion needed beyond Pydantic `datetime` → `str` serialization |
| Pagination over `ingestion_runs` ordered by `started_at` DESC | ✅ Functionally correct; see Finding 1 re: missing index for performance |

---

## Action Items Summary

| Priority | Action | File(s) | Size |
| -------- | ------ | ------- | ---- |
| 🔴 Required | Create Alembic migration `0008_query_support_indexes` with 6 indexes | `libs/db/alembic/versions/0008_query_support_indexes.py` | New file |
| 🔴 Required | Add migration task to `tasks.md` Phase 1 Setup | `specs/014-read-only-fastapi-api/tasks.md` | Task insertion |
| 🔴 Required | Correct `state` value set for `SourceRunOutcomeResponse` | `specs/014-read-only-fastapi-api/data-model.md` | 6-row table update |
| 🔴 Required | Correct `eligibility_state` value set for `SourceEligibilityResponse` | `specs/014-read-only-fastapi-api/data-model.md` | 4-row table update |
| 🔴 Required | Correct `outcome_state` examples for `IngestionRunResponse` | `specs/014-read-only-fastapi-api/data-model.md` | Example text update |
| 🔴 Required | Correct JSON examples and value tables in HTTP contract | `specs/014-read-only-fastapi-api/contracts/phase1-api-contract.md` | JSON + table updates |
| 🟡 Recommended | Document `partial_success` in frontend integration notes | `specs/014-read-only-fastapi-api/contracts/phase1-api-contract.md` | New note |

---

## Appendix: DB Schema Snapshot (Head: 0007_dataset_metadata_topic_tags)

Tables and columns relevant to Phase 1 endpoints as of the current migration head:

```
ingestion_runs
  id                   UUID PK
  run_id               VARCHAR(64) UNIQUE NOT NULL
  trigger_type         VARCHAR(32) NOT NULL
  trigger_origin       VARCHAR(255) NULL          ← added 0005
  lifecycle_state      VARCHAR(32) NOT NULL
  outcome_state        VARCHAR(32) NOT NULL
  started_at           TIMESTAMPTZ NOT NULL
  completed_at         TIMESTAMPTZ NULL
  accepted_count       INTEGER NOT NULL DEFAULT 0
  quarantined_count    INTEGER NOT NULL DEFAULT 0
  failed_count         INTEGER NOT NULL DEFAULT 0
  duplicate_no_op_count INTEGER NOT NULL DEFAULT 0
  conflict_count       INTEGER NOT NULL DEFAULT 0
  due_source_count     INTEGER NOT NULL DEFAULT 0  ← added 0003
  executed_source_count INTEGER NOT NULL DEFAULT 0 ← added 0003
  deferred_source_count INTEGER NOT NULL DEFAULT 0 ← added 0003
  not_due_source_count  INTEGER NOT NULL DEFAULT 0 ← added 0003
  failed_source_count   INTEGER NOT NULL DEFAULT 0 ← added 0003
  [Indexes: PK on id, UNIQUE on run_id]
  [MISSING: index on started_at]

source_run_outcomes
  id                   UUID PK
  run_id               VARCHAR(64) NOT NULL FK→ingestion_runs.run_id
  source_key           VARCHAR(255) NOT NULL
  state                VARCHAR(32) NOT NULL
  accepted_count       INTEGER NOT NULL DEFAULT 0
  quarantined_count    INTEGER NOT NULL DEFAULT 0
  failed_count         INTEGER NOT NULL DEFAULT 0
  duplicate_no_op_count INTEGER NOT NULL DEFAULT 0
  conflict_count       INTEGER NOT NULL DEFAULT 0
  outcome_reason_code  VARCHAR(64) NULL           ← added 0003
  message              TEXT NULL
  [Indexes: PK on id, UNIQUE(run_id, source_key)]

source_eligibility_snapshots
  id                   UUID PK
  run_id               VARCHAR(64) NOT NULL FK→ingestion_runs.run_id
  source_key           VARCHAR(255) NOT NULL
  eligibility_state    VARCHAR(32) NOT NULL
  reason_code          VARCHAR(64) NOT NULL
  evaluated_at         TIMESTAMPTZ NOT NULL
  due_at               TIMESTAMPTZ NULL
  selected_for_execution BOOLEAN NOT NULL DEFAULT false
  lifecycle_state      VARCHAR(32) NOT NULL DEFAULT 'historical_only' ← added 0005
  [Indexes: PK on id, UNIQUE(run_id, source_key)]

conflict_records
  id                   UUID PK
  conflict_id          VARCHAR(64) UNIQUE NOT NULL
  run_id               VARCHAR(64) NOT NULL FK→ingestion_runs.run_id
  source_key           VARCHAR(255) NOT NULL
  series_key           VARCHAR(255) NOT NULL
  reference_period_key VARCHAR(64) NOT NULL
  existing_observation_ref VARCHAR(255) NOT NULL
  incoming_record_ref  VARCHAR(255) NOT NULL
  conflict_type        VARCHAR(64) NOT NULL
  conflict_state       VARCHAR(32) NOT NULL
  created_at           TIMESTAMPTZ NOT NULL
  resolved_at          TIMESTAMPTZ NULL
  [Indexes: PK on id, UNIQUE on conflict_id]
  [MISSING: indexes on run_id, source_key, series_key, reference_period_key, conflict_state]
```
