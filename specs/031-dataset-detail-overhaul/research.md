# Research: Dataset Detail Page Overhaul

## Decision 1: Keep the existing dataset detail API contract and compute view insights in the frontend

- Decision: Reuse the current dataset detail payload shape and derive latest-observation summary, comparative statistics, and movement status in the detail-page presentation layer.
- Rationale: The feature scope is a UI/interaction overhaul, and current contracts already provide ordered observations plus metadata needed for derived display values.
- Alternatives considered:
  - Add a new backend endpoint that precomputes insights: rejected because it expands backend scope and contract risk without required product value for this phase.
  - Embed mockup-only hardcoded metrics in the UI: rejected because it breaks data integrity and cannot scale across datasets.

## Decision 2: Introduce explicit section-level contracts for hero, trend controls, and observed-values table

- Decision: Define stable UI section contracts covering hero attribution/actions, trend range control behavior, and observed-values row semantics.
- Rationale: The page moves from a simple stacked layout to a richer multi-section information architecture; explicit section contracts reduce drift during implementation and testing.
- Alternatives considered:
  - Keep component contracts implicit and rely only on visual styling: rejected because behavior requirements (range switching, movement states, archive access) need testable structure.
  - Merge all detail content into one monolithic component: rejected because it lowers maintainability and weakens targeted testing.

## Decision 3: Keep fallback and not-found behavior consistent with existing discovery patterns

- Decision: Preserve current non-404 error-state rendering and existing not-found handling path while enhancing primary loaded-state presentation.
- Rationale: Existing route behavior is already tested and aligned with discovery UX expectations; redesign should improve loaded-state clarity without changing failure semantics.
- Alternatives considered:
  - Replace fallback behavior with new dedicated screens: rejected because it introduces unnecessary behavioral changes beyond current feature goals.
  - Suppress partial sections on errors while rendering stale content: rejected because stale/partial rendering risks user confusion.

## Decision 4: Use progressive observation disclosure in-table rather than introducing separate navigation for history

- Decision: Keep observed-values inspection anchored on the detail page with a clear archive/load-more affordance for additional rows.
- Rationale: This mirrors mockup intent and keeps users in one context while still exposing deeper history.
- Alternatives considered:
  - Force a separate archive page route: rejected due to extra navigation cost and scope expansion.
  - Show all rows by default: rejected for readability/performance on large histories.

## Decision 5: Reuse shell responsive constraints and typography hierarchy patterns from existing frontend surfaces

- Decision: Implement detail-page responsiveness using established shell width constraints and editorial-type hierarchy conventions already used in discovery pages.
- Rationale: This keeps visual consistency across the product while allowing the dataset detail page to develop a stronger analytical presentation.
- Alternatives considered:
  - Introduce an unrelated page layout system only for detail: rejected because it risks visual drift and maintenance overhead.
  - Keep current minimal card styling: rejected because it does not satisfy the overhaul goals for hierarchy and readability.
