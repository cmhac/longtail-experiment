# Quickstart: Filter Combobox Overhaul

## Goal

Verify that dataset-list filters now behave correctly, searchable combobox narrowing works while typing, and dark-mode hover/active states remain readable.

## Implementation Discipline

Work this feature in small slices. Do not accumulate all changes into one large commit.

Recommended commit sequence:

1. Fix backend/frontend source-category-sort result alignment and commit that slice.
2. Fix combobox in-box option narrowing and commit that slice.
3. Fix dark-mode hover readability, active border treatment, and final regression hardening, then commit that slice.

Before each implementation commit:

1. Run targeted tests for the slice you just changed.
2. Perform the relevant manual browser verification.
3. Run `pre-commit run --all-files`.
4. Run `pnpm exec nx run-many -t test --all`.
5. Run `pnpm exec nx run-many -t coverage --all`.

## Manual Verification Flow

Start from a clean local state:

1. `docker compose down`
2. `docker compose up -d`
3. Confirm the frontend and backend are reachable.

Open the datasets page and verify:

1. Select a source option and confirm the visible dataset rows change to match that source.
2. Select a category option and confirm the visible dataset rows change to match that category.
3. Select a sort option and confirm the visible ordering changes accordingly.
4. Type partial text into the source combobox and confirm the option list narrows.
5. Type partial text into the category combobox and confirm the option list narrows.
6. Type text with no match and confirm a no-match state appears.
7. Clear the typed text and confirm the full option list returns.
8. Switch to dark mode, hover options, and confirm hovered text remains legible.
9. Focus an active combobox and confirm the active state is shown through increased border width.

## Automated Verification Focus

Backend:

- catalog query/service/runtime tests that prove source/category/sort affect returned rows

Frontend:

- dataset list page tests that prove visible rows change after filter selections
- combobox interaction tests that prove typed input narrows available options
- visual-state tests that prove dark-mode hover and active-state behavior where practical

## Expected Outcome

- Filter selections change dataset results instead of only changing the URL.
- Typing inside the comboboxes narrows visible options locally and predictably.
- Dark-mode option hover and active combobox states remain readable and consistent.

## Implementation Notes (2026-03-30)

- Catalog filter normalization now treats sentinel values (such as `all`) as unset across backend service/repository handling.
- Infinite list state now resets when filter query context changes, preventing stale rows from persisting after source/category/sort updates.
- Source/category comboboxes now narrow option lists by typed input, show explicit no-match options, and restore full lists when input is cleared.
- Combobox active state now uses a thicker focus border, and dark-mode option hover text is forced to readable foreground contrast.
