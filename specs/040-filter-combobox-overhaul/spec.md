# Feature Specification: Filter Combobox Overhaul

**Feature Branch**: `[040-filter-combobox-overhaul]`  
**Created**: 2026-03-30  
**Status**: Draft  
**Input**: User description: "we will now overhaul these filters. First, we will fix the existing filter logic so that we can verify that real server-side filtering actually works in frontend and backend. Second, we will fix the filtering in the comboboxes themselves. it's okay for this to remain client-side, but we will need to do a similar process to the combobox filters to ensure that they actually filter the dropdown's options as the user types in the box. third, we will make some ui tweaks. first off, the colors in dark mode are broken. when an option is moused over, the text remains white and is illegible against teh white highlight backround. in addition, the highlight around the box when one is selected by the user is a bit wonky looking. instead of what we do now, we should simply increase the border width of the combobox when it is active."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Apply Real Dataset Filters (Priority: P1)

As a dataset discovery visitor, I can choose source and category filters and receive a dataset list that actually reflects those selections so I can trust the filtering controls.

**Why this priority**: If selected filters do not change the dataset list, the primary discovery workflow is unreliable and the filter controls lose their purpose.

**Independent Test**: Open the datasets page, apply a source or category selection, and verify that the URL state, returned dataset set, and visible rows all match the chosen filter values.

**Acceptance Scenarios**:

1. **Given** the datasets page is loaded with no filters applied, **When** a visitor selects a specific source, **Then** the visible dataset list only contains datasets that belong to that source.
2. **Given** the datasets page is loaded with no filters applied, **When** a visitor selects a specific category, **Then** the visible dataset list only contains datasets that belong to that category.
3. **Given** one or more filters are already active, **When** a visitor changes or clears a filter, **Then** the dataset list refreshes to the correct scope and the visible state matches the current URL state.
4. **Given** a filter selection produces no matching datasets, **When** the refreshed response is rendered, **Then** the page shows the existing empty-results experience instead of stale rows from a previous state.

---

### User Story 2 - Narrow Combobox Options While Typing (Priority: P2)

As a dataset discovery visitor, I can type inside a filter combobox and see the available options narrow to matching entries so I can find a desired filter value quickly.

**Why this priority**: The current controls present themselves as searchable comboboxes, so the in-box filtering behavior must work consistently for the interaction to feel trustworthy and efficient.

**Independent Test**: Open each combobox, type a partial value, and verify that the dropdown options narrow to matching values and that selecting a narrowed option applies the expected filter.

**Acceptance Scenarios**:

1. **Given** a filter combobox contains multiple options, **When** a visitor types text into the combobox input, **Then** the open option list narrows to values that match the typed text.
2. **Given** the typed text has no matching option, **When** the combobox remains open, **Then** the control shows a clear no-match state and does not silently preserve unrelated options as if a match exists.
3. **Given** a visitor narrows the option list by typing, **When** they select one of the remaining options, **Then** the selected value is applied correctly to the dataset list filter.
4. **Given** a visitor clears the typed text, **When** the combobox remains open, **Then** the full set of available options becomes visible again.

---

### User Story 3 - Read And Use Filter Controls In Dark Mode (Priority: P3)

As a visitor using dark mode, I can read hovered combobox options and clearly see which filter control is active so the filter surface remains legible and polished.

**Why this priority**: Once filtering behavior is reliable, visual clarity and focus treatment are the remaining blockers to a polished and usable control surface.

**Independent Test**: In dark mode, open each combobox, hover options, and focus or activate the control to verify readable hover styling and the intended active border treatment.

**Acceptance Scenarios**:

1. **Given** the interface is displayed in dark mode, **When** a visitor hovers an option inside an open combobox, **Then** the option text remains legible against the hover background.
2. **Given** a combobox is focused or actively engaged by the visitor, **When** the active state is shown, **Then** the control communicates that state by increasing border width rather than relying on the current highlight treatment.
3. **Given** a visitor moves focus between filter controls and option lists, **When** active and hover states change, **Then** the controls retain readable contrast and a visually consistent appearance.

### Edge Cases

- A selected source and category combination yields zero datasets and the page must show an empty state without leaving stale rows visible.
- A visitor changes source after category is already selected, causing the previously valid category to have no matching datasets.
- A visitor types a partial match, mixed-case text, or leading/trailing spaces into a combobox search field.
- A visitor types text that matches multiple options with similar names and must still be able to distinguish and select the correct one.
- A visitor types text that matches no option and then removes the text to continue browsing the full option list.
- A visitor uses keyboard navigation rather than a pointer to type, move through narrowed options, and confirm a selection.
- Hover and active styling must remain readable and visually distinct in both light and dark appearance modes.
- The active border-width treatment must not cause layout shift that misaligns neighboring controls or clipped content.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST ensure that source filter selections update the returned dataset list to include only datasets that match the selected source.
- **FR-002**: The system MUST ensure that category filter selections update the returned dataset list to include only datasets that match the selected category.
- **FR-003**: The system MUST keep frontend URL state, backend query handling, and rendered dataset results aligned for every supported filter combination.
- **FR-004**: The system MUST prevent stale dataset rows from remaining visible after a filter selection changes the valid result scope.
- **FR-005**: The system MUST preserve the existing empty-results behavior when a valid filter selection yields no datasets.
- **FR-006**: Each filter combobox MUST narrow its visible option list as the visitor types in the input field.
- **FR-007**: Combobox option narrowing MAY remain local to the already loaded option set, but it MUST behave consistently without requiring a page reload to update the visible option list.
- **FR-008**: The system MUST provide a clear no-match combobox state when the typed filter text does not match any option.
- **FR-009**: Clearing typed combobox input MUST restore the full option list for that control.
- **FR-010**: Selecting an option from a narrowed combobox list MUST apply the same filter result as selecting that option from the full list.
- **FR-011**: In dark mode, hovered combobox options MUST maintain readable contrast between text and background.
- **FR-012**: The active combobox visual treatment MUST use increased border width as the primary active-state signal instead of the current highlight treatment.
- **FR-013**: The updated hover and active styles MUST remain coherent across pointer and keyboard interaction paths.
- **FR-014**: The feature MUST include automated validation for filter result correctness, combobox option narrowing behavior, and visual-state regressions where practical.
- **FR-015**: The feature MUST include manual browser-based validation confirming that each dataset filter control changes visible results as expected.
- **FR-016**: The updated filter experience MUST preserve usability across supported desktop and mobile viewport sizes.

### Key Entities _(include if feature involves data)_

- **Dataset Filter State**: The currently selected source, category, and sort values that define the active dataset listing scope.
- **Catalog Result Scope**: The dataset set returned for the current filter state and rendered on the datasets page.
- **Combobox Option Set**: The available selectable values shown inside each filter combobox before and after the visitor types to narrow them.
- **Combobox Input Match State**: The current typed text, narrowed option subset, and no-match condition for an individual combobox.
- **Filter Control Visual State**: The hover, focus, active, and selected presentations that communicate control status to the visitor.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In manual validation of the source, category, and sort controls, 100% of tested filter selections produce a visible dataset list change that matches the selected state.
- **SC-002**: In automated and manual validation, 100% of sampled filter combinations return dataset rows that are consistent with the active source and category selections.
- **SC-003**: In combobox interaction validation, 100% of tested typed inputs narrow the visible option list to matching values or a clear no-match state within one interaction cycle.
- **SC-004**: In dark-mode UI validation, 100% of audited combobox hover states preserve readable text contrast against their hover backgrounds.
- **SC-005**: In focus and active-state validation, 100% of audited active combobox states use the intended thicker-border treatment without introducing visible layout breakage.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code, and the
  full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before
  commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects, and can satisfy the commit-time coverage stop rule
  (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
- **CA-006 Configuration Integrity**: Any new service or pipeline component that requires
  credentials or external API keys will fail hard (exception/non-zero exit/job-level
  failure) when those variables are absent — no soft outcome recording, no silent
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source
  for any Docker Compose service that requires secrets. (N/A)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI
  components, Tailwind utilities, and shared abstractions in
  `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate
  one-off component patterns or new local CSS without a documented exception.
  (Yes)

## Assumptions

- The overhaul applies to the existing dataset list page filter controls rather than introducing new filter dimensions.
- Source and category filtering are expected to be server-backed for the dataset list itself, while in-box option narrowing may remain local to the client-side option set.
- Sort behavior remains part of the same control surface and should continue to update the visible dataset ordering consistently with the active filter state.
- Existing empty and error states on the datasets page remain the standard fallback experiences unless this feature explicitly changes them.
- The current dark-mode hover and active-state issues are limited to visual treatment and do not require broader shell theme redesign.

## Dependencies

- Existing dataset catalog page and its filter-control interactions.
- Existing discovery catalog response contract and backend catalog filtering behavior.
- Existing browser-based validation workflow used to confirm real dataset filtering outcomes.
- Existing dark-mode theme tokens and control-surface styling patterns already used by the discovery interface.
