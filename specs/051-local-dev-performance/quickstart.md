# Quickstart: Local Development Performance Stabilization (Spec 051)

## Prerequisites

- Dependencies installed and synced for monorepo projects.
- Local Docker daemon running.
- Local stack environment variables configured.

## 1. Baseline local runtime setup

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

## 2. Baseline measurement capture

1. Select a representative dataset sample for detail-page testing (small, medium, large observation histories).
   - Use exactly 9 datasets total: 3 small, 3 medium, 3 large by observation-history size.
2. Capture baseline timings for:
   - first-load dataset detail navigation,
   - repeated refresh sequence (20 loads),
   - related endpoint spot-checks (catalog/search/source/topic/geography).
3. Record baseline data in feature notes for SC-001/SC-002/SC-003 comparison.

### Repeatable timing capture helper

- Use this command to gather comparable local timings for one dataset detail endpoint:
  `python3 - <<'PY'\nimport json,time,urllib.request\nbase='http://127.0.0.1:18081'\ndataset_id='ENERGY.US.ONHIGHWAY_DIESEL.SCA'\nsamples=[]\nfor _ in range(10):\n    start=time.perf_counter()\n    with urllib.request.urlopen(f"{base}/api/datasets/{dataset_id}", timeout=10) as r:\n        payload=json.loads(r.read().decode())\n    samples.append((time.perf_counter()-start)*1000)\nsamples.sort()\nprint({'dataset_id':dataset_id,'median_ms':round(samples[len(samples)//2],2),'p95_ms':round(samples[int(len(samples)*0.95)-1],2),'sample_count':len(samples),'obs_count':len(payload.get('observations',[]))})\nPY`

### Backend detail-path verification commands

1. `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_dataset_detail_targeted_metadata_contract.py`
2. `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_dataset_detail_scope_scaling_contract.py`
3. `uv run --project apps/backend pytest --no-cov apps/backend/tests/integration/test_dataset_detail_local_runtime_latency.py apps/backend/tests/integration/test_dataset_detail_local_latency_improvement.py`

### Frontend detail-page verification commands

1. `pnpm --dir apps/frontend test tests/app/dataset-detail-local-load.test.tsx`
2. `pnpm --dir apps/frontend test tests/app/dataset-detail-trend-error-state.test.tsx`

## 3. Red/green implementation sequence

1. Add failing backend tests for dataset detail retrieval scope and behavioral invariants.
2. Implement backend detail-path performance changes.
3. Add/adjust tests for observation/evidence mapping invariants.
4. Add/adjust frontend integration tests for unchanged detail behavior and loading-state expectations.

## 4. Post-change local verification

1. Restart local stack cleanly:
   - `docker compose down`
   - `docker compose up -d`
2. Re-run the same dataset sample and repeated refresh sequence.
3. Compare results against baseline and verify SC-001/SC-002/SC-003 thresholds.
4. Confirm no functional regressions in related discovery endpoints.

## 5. Quality stop gates (mandatory)

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All commands must pass before commit or handoff.

## 6. Expected outputs

- Verified local detail-page timing improvements aligned to success criteria.
- Passing backend and frontend automated tests covering changed behavior.
- No regressions in related discovery endpoint behavior.

## 7. End-to-end verification runbook

1. Restart stack: `docker compose down && docker compose up -d`
2. Check readiness: `docker compose ps`
3. Validate backend health: `python3 - <<'PY'\nimport urllib.request\nprint(urllib.request.urlopen('http://127.0.0.1:18081/api/health', timeout=10).read().decode())\nPY`
4. Capture detail timings using the repeatable helper for at least two datasets.
5. Run stop gates in order:
   - `pre-commit run --all-files`
   - `pnpm exec nx run-many -t test --all`
   - `pnpm exec nx run-many -t coverage --all`
