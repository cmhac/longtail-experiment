# Data Model: Filter Combobox Overhaul

## Entities

### Dataset Filter State

- **Purpose**: Represents the active dataset-list controls that determine the visible catalog scope.
- **Fields**:
  - `source`: selected source value or default all-sources state
  - `category`: selected category value or default all-categories state
  - `sort`: selected ordering mode
  - `page`: current page state that must reconcile when filters change
- **Rules**:
  - A non-default filter value must change the dataset result scope.
  - Filter changes must invalidate stale page state when needed.
  - URL state and rendered state must match.

### Catalog Result Scope

- **Purpose**: The dataset set returned for the current filter state and rendered on the page.
- **Fields**:
  - `items`: visible dataset rows
  - `total count`: aggregate dataset count shown in page summary
  - `applied filter scope`: source/category/sort context used to generate visible rows
- **Rules**:
  - Visible rows must correspond to the active filter state.
  - Empty results must render as an explicit empty state, not stale content.
  - Sort changes must alter row ordering when the order differs.

### Combobox Option Set

- **Purpose**: The selectable values presented for a filter combobox before and after typing narrows the list.
- **Fields**:
  - `all option`: the default reset option
  - `available values`: selectable source or category values
  - `selected value`: currently applied option
- **Rules**:
  - Clearing input restores the full option set.
  - Selecting from a narrowed set must behave the same as selecting from the full set.

### Combobox Input Match State

- **Purpose**: Captures the transient in-box filtering state while the visitor types.
- **Fields**:
  - `typed text`: current input text
  - `matching options`: narrowed subset that remains visible
  - `no-match flag`: indicates no available option matches the current text
- **Rules**:
  - Matching is driven by the current typed text.
  - No-match state must be explicit when the narrowed set is empty.
  - Resetting typed text returns the control to the full option set.

### Filter Control Visual State

- **Purpose**: Defines the user-visible hover, focus, active, and selected treatments for the combobox controls.
- **Fields**:
  - `default state`
  - `hovered option state`
  - `focused/active control state`
  - `selected option state`
- **Rules**:
  - Dark-mode hovered options must remain readable.
  - Active state must use increased border width.
  - Visual states must remain coherent for pointer and keyboard users.

## Relationships

- `Dataset Filter State` determines the `Catalog Result Scope`.
- `Combobox Option Set` and `Combobox Input Match State` govern how a visitor selects values that update the `Dataset Filter State`.
- `Filter Control Visual State` communicates the status of both the `Combobox Option Set` and the active `Dataset Filter State`.

## State Transitions

### Filter Application

1. Visitor opens a filter control.
2. Visitor selects a source/category/sort value.
3. Dataset filter state updates.
4. Catalog result scope refreshes to match the new state.
5. Empty or populated result state renders accordingly.

### Combobox Narrowing

1. Visitor opens a combobox and types text.
2. Combobox input match state recalculates the visible option subset.
3. Visitor either selects a match, clears the text, or encounters a no-match state.
4. Selecting a match updates dataset filter state; clearing restores full option browsing.

### Active-State Presentation

1. Visitor focuses or actively engages a combobox.
2. Control visual state switches to active.
3. Border width increases to communicate active state.
4. Active treatment clears when focus/engagement ends.
