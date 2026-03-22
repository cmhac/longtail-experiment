# Contract: Schedule State Persistence

**Feature**: 007-schedule-state-persistence
**Owner**: `apps/pipeline/src/orchestration/resources/postgres_run_repository.py`

---

## Method: `read_all_schedule_policies`

### Signature

```python
def read_all_schedule_policies(self) -> dict[str, dict[str, Any]]:
    """Read all persisted schedule policies keyed by source_key."""
```

### Behavior

- Executes a single `SELECT source_key, cadence_type, last_successful_at, next_eligible_at, is_active, priority_class FROM source_schedule_policies ORDER BY source_key ASC`
- Returns a dict where each key is a `source_key` string and each value is a row dict
- If the table is empty, returns `{}`
- Does not raise; propagates DB connection errors to the caller

### Caller Contract

- Called once per `RunCoordinator.run()` invocation before eligibility evaluation
- Called via `getattr(self._run_repository, "read_all_schedule_policies", None)`
- If the method is absent (mock or alternative repo), the read is skipped and all sources default to always-due (safe fail-open)

### Row Schema

| Key                  | Type                           | Notes                           |
| -------------------- | ------------------------------ | ------------------------------- |
| `source_key`         | `str`                          | Matches registration source_key |
| `cadence_type`       | `str`                          | `"hourly"` / `"daily"` / etc.   |
| `last_successful_at` | `datetime` (tz-aware)          | `None` if never written         |
| `next_eligible_at`   | `datetime` (tz-aware) / `None` | Reserved; currently `NULL`      |
| `is_active`          | `bool`                         | Always `True` for active rows   |
| `priority_class`     | `str`                          | Default `"normal"`              |

---

## Method: `upsert_schedule_policy`

### Signature

```python
def upsert_schedule_policy(
    self,
    *,
    source_key: str,
    cadence_type: str,
    last_successful_at: datetime,
    updated_at: datetime,
) -> None:
    """Upsert schedule policy with updated last_successful_at for one source."""
```

### Behavior

- Executes `INSERT INTO source_schedule_policies (...) ON CONFLICT (source_key) DO UPDATE SET last_successful_at = EXCLUDED.last_successful_at, cadence_type = EXCLUDED.cadence_type, updated_at = EXCLUDED.updated_at`
- On first call for a `source_key`: inserts new row with `is_active = true` and `priority_class = "normal"` defaults
- On subsequent calls: overwrites only `last_successful_at`, `cadence_type`, `updated_at`
- Does not raise on upsert; propagates DB connection errors to the caller
- All datetime arguments MUST be timezone-aware

### Caller Contract

- Called once per successful source result after `self._parallel_source_executor.execute()`
- Called only when `source_result.status == "success"` and `registration.schedule_policy is not None`
- Called via `getattr(self._run_repository, "upsert_schedule_policy", None)`
- `last_successful_at` and `updated_at` are both set to the run's `completed_at` timestamp

---

## Wiring: `RunCoordinator._hydrate_schedule_policies`

### Signature

```python
@staticmethod
def _hydrate_schedule_policies(
    registrations: list[SourceWorkflowRegistration],
    db_policies: dict[str, Any],
) -> list[SourceWorkflowRegistration]:
    """Return registrations with last_successful_at patched from persisted DB rows."""
```

### Behavior

- Iterates all registrations; for each one, looks up its `source_key` in `db_policies`
- If a DB row exists and the registration has a non-None `schedule_policy`: patches `last_successful_at` onto the policy via `policy.model_copy(update={...})` and rebuilds the registration via `dataclasses.replace()`
- Returns a new list; input registrations are not mutated
- Sources with no DB row are returned unchanged (policy's `last_successful_at` remains `None`)

### Due-State Impact

With `last_successful_at = None` → `resolve_due_at` returns `evaluated_at` → source is always due.
With `last_successful_at = T` and cadence delta `D` → `resolve_due_at` returns `T + D`.
If `T + D <= now` → source is due. If `T + D > now` → source is not_due.
