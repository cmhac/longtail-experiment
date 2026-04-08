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
