# Quickstart: Home Page Editorial Feed

## Purpose

Validate the editorial recent-updates feed implementation on the homepage, including ordering, row content hierarchy, actions, and fallback states.

## Prerequisites

- Monorepo dependencies installed.
- Backend discovery API runtime available.
- Frontend runtime configured with discovery API base URL.

## 1. Start local runtime

1. Start backend API service for discovery endpoints.
2. Start frontend application service.
3. Confirm homepage and health endpoints load successfully.

## 2. Validate populated editorial feed

1. Open homepage.
2. Confirm section heading reads Recent Updates.
3. Confirm a recency sort cue is visible in section header.
4. Confirm rows display source/date context, title, summary copy, and geography when present.
5. Confirm rows are ordered newest to oldest by latest update timestamp.

## 3. Validate row actions

1. For at least one visible row, confirm action labels View Table and Download CSV are present.
2. Activate View Table and verify expected dataset destination is reached.
3. Activate Download CSV and verify expected dataset export destination is reached.

## 4. Validate theme and responsive behavior

1. Verify feed readability in light mode.
2. Verify feed readability in dark mode.
3. Verify layout stability at common mobile viewport width.
4. Confirm no row overlaps or clipped action labels.

## 5. Validate empty/fallback behavior

1. Simulate empty recent-updates payload and confirm explicit empty-state messaging.
2. Simulate partial/malformed optional row fields and confirm stable row rendering.
3. Simulate feed fetch failure and confirm homepage remains usable with non-blocking fallback.

## 6. Focused automated checks

Suggested commands:

- `pnpm --dir apps/frontend test -- tests/RecentUpdatesFeed.test.tsx tests/home-page.test.tsx tests/DatasetCard.test.tsx`
- `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_dataset_recent_updates_contract.py apps/backend/tests/contract/test_http_runtime_persisted_discovery_endpoints.py`

## 7. Required stop gates

1. `pnpm exec nx run-many -t test --all`
2. `pnpm exec nx run-many -t coverage --all`

## Completion Criteria

- Editorial feed section renders with required hierarchy and recency cue.
- Row actions are present and navigate correctly.
- Empty and fallback states are explicit and non-blocking.
- Monorepo test and coverage stop gates pass.

## Implementation Checklist Notes

- Track task completion directly in `tasks.md` during delivery so each story checkpoint remains independently verifiable.
- Record any command output snippets or observations needed for reviewer verification under the relevant quickstart section when tasks complete.

## Validation Record

- `pre-commit run --all-files`: Passed (lint, format, typecheck, test, coverage, duplication, suppression checks).
- `pnpm exec nx run-many -t test --all`: Passed for `pipeline`, `frontend`, `backend`, and `db` (Nx cache replay).
- `pnpm exec nx run-many -t coverage --all`: Passed for `pipeline`, `frontend`, `backend`, and `db` (Nx cache replay).
