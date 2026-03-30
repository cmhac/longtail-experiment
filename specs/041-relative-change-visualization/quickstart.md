# Quickstart: Relative Change Visualizations

## Goal

Verify that dataset-detail charts can display signed percentage change relative to rolling and fixed baselines while preserving stable behavior in empty/error/invalid-baseline scenarios.

## Mandatory Delivery Discipline

Agents must follow this workflow throughout implementation:

1. Red/green TDD for every behavior slice.
2. Commit regularly (one stable slice per commit).
3. Manually verify functionality in local dev environment after each slice.
4. For frontend slices, manually verify interaction and rendering using browser tools.

Do not defer all work into one large commit.

## Recommended Slice Order

1. Relative-change mode foundation + formula tests.
2. Rolling baseline controls + insufficient-history gap behavior.
3. Fixed baseline by exact available date and index/offset.
4. Baseline persistence across scope changes and unavailable-state behavior.
5. Final regression hardening.

## Red/Green TDD Loop (Each Slice)

1. Add/update failing automated tests first (red).
2. Implement minimal behavior to pass tests (green).
3. Refactor with tests still passing.
4. Run targeted tests for changed scope.
5. Run manual local/browser checks for changed behavior.
6. Run full required gates.
7. Commit the stable slice.

## Required Gates Before Each Commit

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

## Manual Verification Flow

Start clean local environment:

1. `docker compose down`
2. `docker compose up -d`
3. Confirm frontend/backend are reachable.

Then verify in browser tools on a dataset detail page:

1. Switch between observed-value mode and relative-change mode.
2. Confirm relative-change axis/tooltip display percentages.
3. In rolling mode, test offsets 1, 2, 3 and a larger valid offset.
4. Confirm insufficient-history points render as gaps, not fallback numbers.
5. In fixed mode, test baseline selection by:
   - exact available date
   - observation index/offset
6. Confirm date selector shows only available observation dates.
7. Confirm signed formula behavior (positive/negative changes) on sampled points.
8. Change chart time range/filter scope and verify baseline settings:
   - preserved when valid
   - visible with explicit unavailable state when invalid
9. Confirm existing empty/error/not-found behaviors remain intact.

## Expected Outcome

- Relative-change mode is reliable, interpretable, and regression-safe.
- Baseline workflows behave deterministically and transparently.
- Implementation history remains reviewable via regular stable commits.
- All quality and coverage gates pass before each commit and final handoff.
