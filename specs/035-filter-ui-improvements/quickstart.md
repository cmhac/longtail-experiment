# Quickstart: Filter UI Improvements

## Prerequisites

- Monorepo dependencies installed.
- Frontend app runnable locally.

## 1. Run Focused Frontend Validation During Development

1. Run frontend unit/integration tests for discovery controls and dataset list pages.
2. Run frontend linting/type checks for changed files.

## 2. Manual Verification Flow

1. Start from clean local runtime state where needed and open the dataset list page.
2. Verify filter container background aligns with shared filter/shell surface styling.
3. Verify all three selector controls render and behave as combo-box style controls.
4. Verify layout expectations:
   - Two filtering controls grouped on the left.
   - Sorting control separated on the right.
   - Controls use capped widths and do not stretch to full row width.
5. Verify responsive behavior:
   - Narrow viewport reflow remains understandable and usable.
6. Verify interaction outcomes:
   - Filter changes update dataset results as expected.
   - Sort changes update ordering as expected.
   - Empty/no-match states remain explicit.

## Story-Level Verification Checklist

### Task 1 - Filter Container Surface Alignment

- Filter control container background matches shared filter surface style.
- Text, borders, and focus visibility remain readable in supported appearance modes.

### Task 2 - Selector Modernization

- All in-scope controls use combo-box style interactions.
- Existing filter/sort semantics and selected value behavior remain unchanged.

### Task 3 - Layout Grouping and Spacing

- Two filter selectors appear as a left group.
- Sort selector appears as a right-separated group where width allows.
- Selector widths remain capped and avoid full-row expansion in standard desktop layouts.

## 3. Required Quality Gates Before Commit

1. `pnpm exec nx run-many -t test --all`
2. `pnpm exec nx run-many -t coverage --all`
3. `pre-commit run --all-files`

## 4. Documentation Verification

1. Confirm plan artifacts (`research.md`, `data-model.md`, `contracts/`, `quickstart.md`) reflect final scope.
2. Confirm spec scope remains aligned with implemented behavior for all three tasks.
3. Confirm workflow and command references stay consistent with repository conventions.
