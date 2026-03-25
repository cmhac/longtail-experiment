# Research: Unified Search Page Experience

## Decision 1: Use route-based query state as the canonical search context

- Decision: Treat dedicated search route query parameters as the canonical source of truth for submitted search state.
- Rationale: A single URL-carried query context unifies homepage and navbar entry points, supports shareable/searchable navigation state, and removes duplicate inline search execution paths.
- Alternatives considered:
  - Keep homepage inline results and optionally mirror to route state: rejected because it preserves split behavior and inconsistent user expectations.
  - Use transient client-only state for query transport: rejected because it breaks deep-linkability and refresh resilience.

## Decision 2: Build one reusable search interaction surface with entry-point wrappers

- Decision: Factor search typing/submit/suggestion behavior into a reusable search surface contract, then wrap it with homepage hero styling, dedicated-page centered styling, and navbar compact-expand styling.
- Rationale: Shared interaction logic enforces consistent behavior while allowing each surface to retain context-appropriate presentation.
- Alternatives considered:
  - Duplicate search logic in homepage/navbar/search page: rejected due to drift risk and higher maintenance cost.
  - Force one identical visual component across all surfaces: rejected because navbar needs compact behavior that differs from hero/page layouts.

## Decision 3: Preserve existing discovery search contracts and result hierarchy

- Decision: Keep existing search query, summary, and suggestion backend/frontend contracts unchanged; only change where and how the user enters and lands into search.
- Rationale: This feature is interaction and navigation unification, not search relevance or data-contract redesign.
- Alternatives considered:
  - Introduce a new backend search contract for dedicated page: rejected because it adds risk without user-facing value for this scope.
  - Rewrite result presentation to a new hierarchy: rejected because requirement explicitly asks to mirror the existing homepage search/results layout.

## Decision 4: Define explicit fallback states for empty, idle, and error flows

- Decision: Require clear dedicated-page states for no query, no results, and backend request failure while keeping input active for immediate retry.
- Rationale: Route-based search introduces direct-entry scenarios (empty query in URL or failed fetch) that must remain usable.
- Alternatives considered:
  - Redirect empty queries back to homepage: rejected because dedicated search page should remain a stable search destination.
  - Hide search input on errors: rejected because this blocks recovery.
