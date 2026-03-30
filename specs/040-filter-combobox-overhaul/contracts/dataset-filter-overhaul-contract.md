# Dataset Filter Overhaul Contract

## Scope

This contract governs the dataset-list filter controls on the datasets page, including:

- source/category/sort result alignment
- searchable combobox option narrowing
- dark-mode hover readability
- active-state visual treatment

## Result-Alignment Contract

- Selecting a source updates the visible dataset rows to the corresponding source scope.
- Selecting a category updates the visible dataset rows to the corresponding category scope.
- Selecting a sort mode updates visible dataset ordering when the requested ordering differs from the current ordering.
- Sentinel values (`all` and whitespace-only variants) are treated as unset filters and must not accidentally restrict catalog results.
- URL state, backend filter handling, and rendered rows must remain aligned after each selection.
- When a filter combination yields zero matches, the page renders the explicit empty-results experience instead of stale prior rows.
- Changing filter query context resets infinite list state to the server-returned first page so stale rows are never retained.

## Combobox Narrowing Contract

- Typing inside an open filter combobox narrows the visible option list to matching entries from the available option set.
- Clearing typed text restores the full option list.
- A no-match state is explicit when the typed text leaves no visible options.
- Selecting an option from the narrowed set applies the same filter behavior as selecting that option from the full set.

## Visual-State Contract

- In dark mode, hovered option text remains legible against the hover background.
- Active combobox state is communicated through increased border width.
- Hover, focus, active, and selected states remain understandable for pointer and keyboard interaction paths.

## Regression Contract

- The overhaul must not leave stale rows visible after a filter change.
- The overhaul must not break existing empty-state and error-state experiences.
- The overhaul must not introduce a new one-off styling system outside the existing shared discovery control surface.
- The implementation must be deliverable in incremental commits rather than one large commit, with each commit representing a stable behavior or UI slice.
