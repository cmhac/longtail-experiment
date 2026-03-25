# Quickstart: Dataset List Page

## Purpose

Validate the datasets listing page experience, including hierarchy, controls, card metadata, and primary actions.

## Prerequisites

- Monorepo dependencies installed.
- Backend discovery API runtime available.
- Frontend runtime configured with discovery API base URL.

## 1. Start local runtime

1. Start backend API service for discovery endpoints.
2. Start frontend application service.
3. Confirm homepage and datasets routes load successfully.

## 2. Validate page hierarchy

1. Open `/datasets`.
2. Confirm page heading reads "Datasets".
3. Confirm total-series summary is visible below or near heading.
4. Confirm request-new-dataset action is visible in the page header region.

## 3. Validate listing controls

1. Confirm source filter includes all-sources plus specific source options.
2. Confirm category filter includes all-categories plus specific category options.
3. Confirm sort control defaults to recency-focused ordering.
4. Change each control and verify visible list updates accordingly.

## 4. Validate dataset cards

1. Confirm each visible card includes source label, title, summary, tags, and last-updated context.
2. Confirm save/share action affordances are visible for each card.
3. Confirm cards maintain stable spacing and readable hierarchy while scrolling.

## 5. Validate empty and fallback behavior

1. Select control combinations that yield no matches and confirm explicit empty-results messaging.
2. Simulate missing optional metadata and confirm cards remain stable.
3. Simulate list fetch failure and confirm non-blocking fallback behavior with retained page usability.

## 6. Validate responsive behavior

1. Verify desktop readability and control alignment.
2. Verify mobile readability and wrapped controls/card content.
3. Confirm no clipped text or overlapping actions at small viewport widths.

## 7. Focused automated checks

Suggested commands:

- `pnpm --dir apps/frontend test -- tests/datasets-page.test.tsx tests/discovery-client.test.ts tests/shell-structure-contract.test.tsx`
- `pnpm --dir apps/frontend typecheck`
- `pnpm --dir apps/frontend exec biome check .`

## 8. Required stop gates

1. `pnpm exec nx run-many -t test --all`
2. `pnpm exec nx run-many -t coverage --all`

## Completion Criteria

- Datasets page renders required heading, summary, controls, and card metadata.
- Control interactions produce expected list state transitions.
- Empty/fallback states remain explicit and non-blocking.
- Monorepo test and coverage stop gates pass.

## Implementation Checklist Notes

- Confirmed datasets page contract checkpoints: heading/total summary, request CTA, controls strip, card metadata, empty/fallback behavior.
- Confirmed URL-driven control state contract for `source`, `category`, and `sort` query parameters.
- Confirmed duplicate dataset suppression in rendered list output.

## Validation Record

- Focused frontend tests passed:
  - `pnpm --dir apps/frontend test -- tests/DatasetCatalogList.test.tsx tests/DatasetCard.test.tsx tests/datasets-page.test.tsx tests/discovery-client.test.ts tests/shell-structure-contract.test.tsx`
- Focused interaction tests passed:
  - `pnpm --dir apps/frontend test -- tests/DatasetListControls.test.tsx tests/datasets-page.test.tsx`
- Frontend quality checks passed:
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Manual runtime verification (fallback state):
  - Started frontend with unreachable API base and confirmed `/datasets` renders heading, request CTA, and non-blocking error state.
- Manual runtime verification (populated state):
  - Started local stack with `docker compose up -d db backend` and frontend with `DISCOVERY_API_BASE_URL=http://localhost:8080`.
  - Opened `/datasets` and confirmed populated list rendering with controls, total-series summary, metadata-rich cards, and save/share actions.
- Monorepo stop gates passed:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`
- Final repository quality gate passed:
  - `pre-commit run --all-files`
