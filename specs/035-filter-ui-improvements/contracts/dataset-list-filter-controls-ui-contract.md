# Dataset List Filter Controls UI Contract

## Scope

This contract governs the dataset-list filter control row presentation and interactions, including container surface styling, selector control type, and selector layout grouping.

## Surface Contract

- The filter control container uses the approved shared filter/shell surface styling semantics.
- Surface readability remains preserved across supported appearance modes.
- Container state transitions (default, active selection, loading-visible, no-match context) preserve consistent background intent.

## Selector Contract

- The three selector controls on the dataset list row use combo-box style interactions.
- Selector role assignment is fixed:
  - Two selectors are filtering controls.
  - One selector is the sorting control.
- Selector migration does not alter:
  - Filter value meaning.
  - Sort value meaning.
  - Existing result-update semantics for user selections.

## Layout Contract

- Control row grouping:
  - Left group: the two filtering selectors.
  - Right group: the sorting selector.
- A visible spacing separation exists between left and right groups where horizontal space allows.
- Selector widths are capped and do not expand to fill the full row width under normal desktop-width conditions.
- On narrow viewports, controls may reflow, but grouping intent and control usability remain understandable.

## Accessibility and Operability Contract

- Selector controls remain keyboard operable for open, option navigation, and selection confirmation paths.
- Focus visibility remains clear after style and layout updates.
- Selected values remain legible in all supported appearance modes.

## Regression Contract

- Filtering and sorting outcomes remain functionally equivalent to pre-change behavior.
- Empty-result and loading-visible states remain explicit and readable.
- No control-level change introduces result mismatches relative to selected filter/sort values.

## Rollout Status

- Surface contract: implemented
- Selector contract (combo-box controls): implemented
- Layout contract (left filter group / right sort group / capped widths): implemented
- Accessibility and operability checks: covered by focused selector interaction tests and keyboard-flow assertions
