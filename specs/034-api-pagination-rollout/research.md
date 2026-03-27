# Phase 0 Research: Discovery Pagination Rollout

## Decision 1: Standardize page-based pagination metadata across all discovery list routes

- Decision: Use one shared pagination response shape for all in-scope list routes: `items`, `page`, `page_size`, `total_items`, `total_pages`, and existing route-specific metadata.
- Rationale: A consistent metadata contract simplifies frontend controls, reduces route-specific branching, and improves testability across backend and frontend.
- Alternatives considered:
  - Keep mixed route-specific metadata shapes: rejected because it increases client complexity and drift risk.
  - Introduce cursor-only contract: rejected for this rollout due to broad existing page/page_size usage and migration overhead.

## Decision 2: Keep stable deterministic ordering as a pagination invariant

- Decision: Every paginated route enforces deterministic ordering within the filtered scope before slicing pages.
- Rationale: Stable ordering prevents duplicate/skip behavior while users navigate between pages.
- Alternatives considered:
  - Paginate without explicit sort guarantees: rejected due to non-deterministic cross-page navigation.
  - Route-specific ad hoc ordering changes: rejected because it introduces inconsistent user experience.

## Decision 3: Treat source/topic/geography dataset lists as in-scope list routes

- Decision: Apply page-based pagination to source detail, topic detail, and geography detail dataset collections.
- Rationale: These routes currently return full list payloads and represent high-risk unbounded list surfaces.
- Alternatives considered:
  - Keep these routes unpaginated and only paginate search/catalog: rejected because feature scope explicitly targets any list-type request.
  - Add frontend-only slicing for these routes: rejected because it still transfers unbounded payloads.

## Decision 4: Replace frontend oversized one-page fetch behavior with explicit page state

- Decision: Remove large static page-size fetch strategy and drive list rendering from selected page, page size, and metadata-backed controls.
- Rationale: Explicit page state aligns UI behavior with backend contracts and avoids hidden payload growth.
- Alternatives considered:
  - Keep large one-page fetch and only display controls: rejected because controls would be cosmetic and not reduce payload size.
  - Infinite scroll only: rejected for this feature because requirements call for route-level API-based pagination semantics.

## Decision 5: Keep route-level page-size defaults with centralized validation bounds

- Decision: Preserve existing validated defaults where already established and align remaining list routes to validated min/max bounds documented in contracts.
- Rationale: This avoids surprise behavior changes while enforcing safe limits consistently.
- Alternatives considered:
  - One global page-size default for every route immediately: rejected because some route expectations may differ and require staged alignment.
  - No explicit validation on new paginated routes: rejected due to error-handling and contract ambiguity.

## Decision 6: Verify rollout with contract/runtime tests plus frontend integration tests

- Decision: Extend backend contract/runtime tests and frontend page/client tests to cover page navigation, out-of-range behavior, and filter interaction resets.
- Rationale: Pagination is cross-cutting and susceptible to regressions that unit tests alone may miss.
- Alternatives considered:
  - Rely only on manual testing: rejected due to high regression risk and coverage requirements.
  - Add tests only to changed routes: rejected because shared pagination behavior must be enforced across all in-scope list routes.
