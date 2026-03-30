# Research: Unified Feed List Components

## Decision 1: Use one grouped component module for the shared feed/list primitives

- Decision: Create the new feed/list UI as one grouped discovery component module that exports the wrapper, optional title region, row, metadata rail, title, subtitle, update date, and display-category primitives from a single place.
- Rationale: The constitution explicitly favors shared abstractions for repeated frontend patterns, and the existing `PageHeader` module already establishes the repository pattern of grouped composable exports for related UI pieces. A grouped module keeps the relationship between these primitives obvious and reduces the risk of near-duplicate wrapper and row implementations drifting apart.
- Alternatives considered:
  - Keep separate standalone files for every primitive: rejected because the feature is specifically about one coherent repeated pattern and would fragment ownership.
  - Add a second generic UI package: rejected because this pattern is discovery-specific and belongs in the existing frontend component area.

## Decision 2: Preserve the current editorial grid anatomy as the baseline layout

- Decision: Treat the current shared two-column editorial row shape already present in `UnifiedDatasetRow` and `SourceListRow` as the layout baseline for the new primitives.
- Rationale: The current source and dataset rows already converge on the same grid, spacing, typography scale, and responsive collapse. Reusing that structure minimizes visual drift, keeps the refactor regression-safe, and satisfies the feature goal without introducing a second redesign effort.
- Alternatives considered:
  - Redesign the row from scratch: rejected because the spec is about reuse and component structure, not visual rework.
  - Normalize every list surface into a generic table-like layout: rejected because it would move away from the established editorial browsing hierarchy.

## Decision 3: Introduce a flexible display-category field as presentation-only metadata

- Decision: Model “display category” as a generic presentation field rendered above the date in the left metadata rail, with each consuming surface responsible for mapping its own source data into that field.
- Rationale: Existing surfaces already need different values in that position, such as source name or source type. Treating the field as presentation-only keeps the shared primitives generic and avoids polluting backend or API contracts with a new business concept that does not need persistence.
- Alternatives considered:
  - Hardcode the left-rail top line as source label or source type: rejected because it would not cover both current source and dataset list use cases.
  - Add multiple dedicated props for each possible left-rail label type: rejected because it would create an inflexible API and push surface-specific semantics into the shared component contract.

## Decision 4: Keep mapper and adapter logic outside the shared presentation primitives

- Decision: Keep formatting and normalization logic, such as date formatting, fallback summary assembly, and geography/tag cleanup, in existing mapper or adapter layers rather than embedding that logic inside the new feed/list primitives.
- Rationale: The shared component group should own structure and presentation hierarchy, not surface-specific payload shaping. Existing files like `unified-dataset-row-mappers.ts` already hold these responsibilities, and preserving that separation will make the shared primitives easier to reuse for both dataset and source rows.
- Alternatives considered:
  - Move all normalization into the new primitives: rejected because it would couple presentation with source-specific data rules.
  - Duplicate mapping logic in each consumer: rejected because it would recreate the duplication this feature is meant to remove.

## Decision 5: Preserve current fallback ownership outside the shared component group

- Decision: Leave empty, unavailable, and error-state components owned by the current page or surface wrappers rather than forcing the new feed/list group to absorb those states.
- Rationale: Current surfaces already distinguish between populated state and broader request-state handling. Keeping fallback ownership outside the shared group preserves clean boundaries, avoids overloading the new component API, and lets the group focus on rendering populated list/feed UI.
- Alternatives considered:
  - Make the shared wrapper own all populated and fallback states: rejected because it would mix request semantics with presentation primitives.
  - Duplicate fallback handling during migration: rejected because the repository already has established shared `EmptyState` and `ErrorState` components.
