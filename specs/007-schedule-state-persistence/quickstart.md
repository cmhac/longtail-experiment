# Quickstart: Schedule State Persistence

**Feature**: 007-schedule-state-persistence
**Prerequisites**: Local DB running (`docker compose up -d`), migrations applied through `0003_sched_eligibility`

## Verification Sequence

This quickstart verifies the complete scheduling lifecycle:

1. First run — all sources due (no prior history) + DB populated
2. Immediate re-run — all sources not_due (cadence gate active)
3. Backdate one source — targeted source becomes due again
4. Re-run — only the backdated source executes

---

### Step 1: Reset all schedule state

```bash
# Clear all runtime tables including source_schedule_policies
uv run --project apps/pipeline python -c "
import sys; sys.path.insert(0, 'apps/pipeline')
from src.orchestration.definitions import get_ingest_runtime
get_ingest_runtime().run_repository.clear_all()
print('cleared')
"
```

Expected: `cleared`

---

### Step 2: Run the pipeline (first run — all sources due)

```bash
uv run --project apps/pipeline python tools/quality/verification/verify_schedule.py
```

Expected output (approximate):

```
due_source_count: 3
executed_source_count: 3
not_due_source_count: 0
  dummy_source: due selected=True
  example_source: due selected=True
  fred_fedfunds: due selected=True
fred_fedfunds last_successful_at after run: 2026-03-22 13:32:51.777413+00:00
```

---

### Step 3: Run immediately again (all sources not_due)

```bash
uv run --project apps/pipeline python tools/quality/verification/verify_schedule.py
```

Expected output:

```
due_source_count: 0
executed_source_count: 0
not_due_source_count: 3
  dummy_source: not_due selected=False
  example_source: not_due selected=False
  fred_fedfunds: not_due selected=False
```

---

### Step 4: Inspect schedule state in DB

```sql
SELECT source_key, cadence_type, last_successful_at, updated_at
FROM source_schedule_policies
ORDER BY source_key;
```

Expected: 3 rows (dummy_source, example_source, fred_fedfunds) with recent timestamps.

---

### Step 5: Backdate fred_fedfunds to force re-due

```sql
UPDATE source_schedule_policies
SET last_successful_at = NOW() - INTERVAL '2 days'
WHERE source_key = 'fred_fedfunds';
```

---

### Step 6: Run again (only fred_fedfunds is due)

```bash
uv run --project apps/pipeline python tools/quality/verification/verify_schedule.py
```

Expected output:

```
due_source_count: 1
executed_source_count: 1
not_due_source_count: 2
  dummy_source: not_due selected=False
  example_source: not_due selected=False
  fred_fedfunds: due selected=True
fred_fedfunds last_successful_at after run: 2026-03-22 13:33:44.840966+00:00
```

---

## Useful SQL Commands

### Inspect current schedule state

```sql
SELECT source_key, cadence_type, last_successful_at, updated_at
FROM source_schedule_policies
ORDER BY source_key;
```

### Force a source to be due immediately

```sql
UPDATE source_schedule_policies
SET last_successful_at = '1970-01-01 00:00:00+00'
WHERE source_key = 'fred_fedfunds';
```

### Reset all sources to always-due (clears entire table)

```sql
DELETE FROM source_schedule_policies;
```

### Check eligibility outcomes for the most recent run

```sql
SELECT ses.source_key, ses.eligibility_state, ses.selected_for_execution, ses.due_at
FROM source_eligibility_snapshots ses
JOIN ingestion_runs ir ON ses.run_id = ir.run_id
WHERE ir.started_at = (SELECT MAX(started_at) FROM ingestion_runs)
ORDER BY ses.source_key;
```

---

## Quality Gate

```bash
# Full pipeline quality gate (must pass at ≥90% coverage)
uv run --project apps/pipeline pytest apps/pipeline/tests \
  --cov=apps/pipeline/src \
  --cov-fail-under=90 \
  -q

# Targeted: schedule policy persistence tests only
uv run --project apps/pipeline pytest \
  apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py \
  apps/pipeline/tests/orchestration/test_run_coordinator.py \
  -v
```

## Observed Results (2026-03-22)

- 100 tests passed
- 93.31% total coverage
- Run 1 (clean slate): 3 sources due, 3 executed, `source_schedule_policies` populated
- Run 2 (immediate): 0 due, 3 not_due — cadence enforcement confirmed
- Backdate `fred_fedfunds` by 2 days → Run 3: 1 due (fred_fedfunds), 2 not_due — selective due confirmed
- `fred_fedfunds.last_successful_at` updated to run completion time after Run 3
