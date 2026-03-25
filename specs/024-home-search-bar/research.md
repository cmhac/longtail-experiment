# Research: Homepage Search Bar Experience

## Decision 1: Summary counts contract shape

- Decision: Provide homepage scope summary as explicit backend response fields for active dataset count and active source count, consumed directly by the homepage search surface.
- Rationale: Keeps frontend display logic simple and deterministic while making data ownership explicit in backend contracts.
- Alternatives considered:
  - Hardcoded placeholder replacement in frontend only: does not satisfy runtime real-value requirement.
  - Reusing unrelated metadata endpoints: increases coupling and weakens contract clarity.

## Decision 2: Likely-match suggestion behavior

- Decision: Add likely-match suggestions as a dedicated query path optimized for partial input and short result lists.
- Rationale: Suggestion UX has different behavior and latency expectations than full paginated search.
- Alternatives considered:
  - Reusing full search endpoint for every keypress: heavier payload and unnecessary pagination overhead.
  - Client-side fuzzy matching only: misses canonical backend ranking and source-of-truth consistency.

## Decision 3: Trigram-backed matching strategy

- Decision: Use PostgreSQL trigram similarity behavior for likely-match ranking against dataset title/id text, with stable ordering and bounded result counts.
- Rationale: Aligns with requirement for likely matches using trigram semantics and supports typo-tolerant discovery.
- Alternatives considered:
  - Prefix-only matching: fast but poor tolerance for misspellings and infix user input.
  - Exact-match-first only: too restrictive for exploratory typing behavior.

## Decision 4: Frontend interaction model

- Decision: Keep the search bar centered in the homepage hero area and render suggestions in a dropdown anchored to the input, updated from latest query text.
- Rationale: Preserves visual prominence requirement and supports fast iterative query refinement.
- Alternatives considered:
  - Inline results below the full page content: weak immediate feedback and less focused interaction.
  - Replacing existing recent updates area with only suggestions: reduces browsing value outside active typing.

## Decision 5: Graceful fallback semantics

- Decision: If summary/suggestions cannot be loaded, preserve input usability and show safe fallback text/state rather than blocking discovery entry.
- Rationale: Home search entry point must remain usable even during partial backend issues.
- Alternatives considered:
  - Blocking search interactions until summary loads: poor resilience and unnecessary coupling.
  - Silent failure with stale data retained indefinitely: can mislead users about current searchable scope.

## Decision 6: Test strategy

- Decision: Add backend contract/query tests for summary+suggestions and frontend tests for centered layout, runtime count rendering, dropdown updates, and no-stale-suggestion behavior.
- Rationale: This feature crosses layers and needs contract plus UX validation to prevent regressions.
- Alternatives considered:
  - Frontend-only tests: misses backend ranking/aggregation contract integrity.
  - Manual verification only: insufficient for constitution quality and coverage requirements.
