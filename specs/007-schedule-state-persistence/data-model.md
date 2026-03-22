# Data Model: Schedule State Persistence

**Feature**: 007-schedule-state-persistence
**Migration**: `0003_sched_eligibility` (already applied — no new migration required)

## Entities

### SourceSchedulePolicy

Durable record of one source's cadence type and last successful execution timestamp.
One row per registered source key. The table is authoritative for last-run history;
in-code registration provides current cadence type which is synced on each upsert.

**Table**: `source_schedule_policies`

| Column               | Type                     | Nullable | Default    | Notes                                                               |
| -------------------- | ------------------------ | -------- | ---------- | ------------------------------------------------------------------- |
| `id`                 | UUID                     | No       | `gen_uuid` | Synthetic primary key                                               |
| `source_key`         | VARCHAR(255)             | No       | —          | Unique; matches `SourceWorkflowRegistration.source_key`             |
| `cadence_type`       | VARCHAR(32)              | No       | —          | `"hourly"`, `"daily"`, `"weekly"`, `"monthly"`, `"custom_interval"` |
| `cadence_value`      | INTEGER                  | Yes      | `NULL`     | Only for `custom_interval`; hours                                   |
| `timezone`           | VARCHAR(64)              | No       | `"UTC"`    | Not currently used in due-state computation                         |
| `is_active`          | BOOLEAN                  | No       | `true`     | Set false to exclude source from scheduling without deregistering   |
| `last_successful_at` | TIMESTAMP WITH TIME ZONE | Yes      | `NULL`     | Written by coordinator after each successful run                    |
| `next_eligible_at`   | TIMESTAMP WITH TIME ZONE | Yes      | `NULL`     | Reserved for explicit override scheduling; not computed currently   |
| `priority_class`     | VARCHAR(32)              | No       | `"normal"` | Reserved for future priority-queue use                              |
| `updated_at`         | TIMESTAMP WITH TIME ZONE | No       | —          | Set to run `completed_at` on each upsert                            |

**Unique Constraint**: `source_key`
**Conflict Strategy**: `ON CONFLICT (source_key) DO UPDATE` — idempotent upsert; only `last_successful_at`, `cadence_type`, and `updated_at` are overwritten.

### ScheduleHydrationContext (in-memory only, not persisted)

A transient merge of the DB row and the in-code `SourceSchedulePolicy` Pydantic model.
Produced by `_hydrate_schedule_policies()` in `RunCoordinator` before each scheduled
evaluation. Not stored; rebuilt on every run.

| Field                | Source                        | Notes                                                |
| -------------------- | ----------------------------- | ---------------------------------------------------- |
| `source_key`         | Code registration             | —                                                    |
| `cadence_type`       | Code registration             | DB value is overwritten on upsert; code is canonical |
| `last_successful_at` | DB row (`last_successful_at`) | Merged in from DB; `None` if no row exists           |
| `is_active`          | Code registration             | Not read from DB currently                           |

## Relationships

```
SourceWorkflowRegistration (in-memory)
  1 ─── 0..1 ──► SourceSchedulePolicy (DB row)
                  merged into ScheduleHydrationContext
                  used by DueSourceSelector.evaluate_scheduled()
```

## State Transitions

```
[No DB row]      ──► source always due (last_successful_at = None)
[Row exists]     ──► due if now >= last_successful_at + cadence_delta(cadence_type)
[Row updated]    ──► after successful run: last_successful_at = completed_at
[Row cleared]    ──► DELETE reverts source to always-due state
[Row backdated]  ──► UPDATE last_successful_at to force re-due
```
