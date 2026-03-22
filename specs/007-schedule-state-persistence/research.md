# Research: Schedule State Persistence

**Feature**: 007-schedule-state-persistence
**Date**: 2026-03-22

## Decision Log

### Decision 1: No new migration required

**Decision**: Use the existing `source_schedule_policies` table created in
`0003_sched_eligibility`.

**Rationale**: The table was designed specifically for this purpose with all required
columns. Creating a new migration would create a spurious schema version bump with no
schema change.

**Alternatives considered**:

- New migration adding a dedicated `source_last_run` table → rejected; redundant and
  confusing given the existing table already captures this exactly.

---

### Decision 2: Read all policies in a single SELECT, not per-source

**Decision**: `read_all_schedule_policies()` fetches all rows in one query and returns
a dict keyed by source_key. The coordinator does a dict lookup per registration.

**Rationale**: The number of registered sources is small (dozens to low hundreds).
A single `SELECT * FROM source_schedule_policies` is cheaper than N individual queries.
This also allows the read to be a single unit-of-work inside one DB connection.

**Alternatives considered**:

- Per-source `SELECT ... WHERE source_key = :key` inside the coordinator loop → rejected;
  N+1 query pattern; unnecessary for a small source registry.

---

### Decision 3: Use `completed_at` as `last_successful_at`

**Decision**: After successful source execution, record the run's `completed_at`
timestamp as `last_successful_at`, not the observation timestamp from the source data.

**Rationale**: `completed_at` is always available and consistently typed (timezone-aware
datetime). Observation timestamps vary by source and may not reflect when the fetch
occurred. Using run completion time also aligns with "when did we last check this
source" semantics, which is what cadence enforcement cares about.

**Alternatives considered**:

- Use the latest observation date from the fetched data → rejected; not always
  available, creates source-specific special-casing, and conflates data recency with
  run-execution recency.
- Use `started_at` → rejected; doesn't reflect that the source actually completed
  successfully within the run.

---

### Decision 4: Duck-typed `getattr` access pattern for repo methods

**Decision**: New repo methods are called via `getattr(self._run_repository, "read_all_schedule_policies", None)` in `RunCoordinator`, matching the pattern already used for `add_run_outcome` and `write_eligibility_snapshots`.

**Rationale**: Preserves backward compatibility — callers using a mock or alternative
run_repository implementation will not break if the new methods are absent; they simply
skip the read/write. No new Protocol or ABC is needed.

**Alternatives considered**:

- Define a `SchedulePolicyRepository` Protocol and type-check `isinstance` → rejected;
  adds an abstraction not needed at this scale; all tests can mock the duck-typed
  pattern adequately.
- Make read/write a hard dependency with a non-optional constructor argument → rejected;
  would break all existing tests that pass `run_repository=None` or a minimal mock.

---

### Decision 5: Write only on `"success"` status

**Decision**: `upsert_schedule_policy` is called only for source results with
`status == "success"`. Failed, deferred, and not-due outcomes do not update the record.

**Rationale**: The purpose of `last_successful_at` is to record when the source's data
was last successfully refreshed. A failed run did not refresh the data, so updating
the timestamp would cause the source to be incorrectly skipped on the next due cycle.

**Alternatives considered**:

- Write on any execution (including failure) to advance "last attempted at" → rejected;
  conflates attempt time with success time; would suppress retry of failed sources.
- Write a separate `last_attempted_at` column in addition to `last_successful_at` →
  deferred; useful for diagnostics but not needed to close the cadence enforcement gap.

---

### Decision 6: `is_active`, `priority_class`, `cadence_value` use DB defaults on insert

**Decision**: On the first INSERT (when no prior row exists), `is_active = true`,
`priority_class = "normal"`, and `cadence_value = NULL` are written via SQL defaults.
Subsequent upserts only update `last_successful_at`, `cadence_type`, and `updated_at`.

**Rationale**: These fields are reserved for future scheduling extensions. Writing them
on every upsert would create coupling between the coordinator write path and schema
fields that are not yet consumed. Keeping the upsert focused on the timing fields
reduces blast radius of future schema changes.

**Alternatives considered**:

- Write all fields on every upsert → rejected; unnecessary coupling; makes it harder
  to introduce per-source active/inactive controls in future without coordinator changes.
