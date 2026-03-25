# Research: Home Page Editorial Feed

## Decision 1: Editorial list replaces card stack

- Decision: Render Recent Updates as an editorial row list with clear typographic hierarchy rather than generic card tiles.
- Rationale: The target experience prioritizes fast scanning of source/date/title/summary over card chrome and dense borders.
- Alternatives considered:
  - Keep card components and adjust spacing only: insufficient for the required editorial look and hierarchy.
  - Replace section with a dense table: reduces readability and visual narrative quality on the homepage.

## Decision 2: Keep recency-first ordering and explicit sort cue

- Decision: Preserve descending latest-update ordering and render a visible sorted-by-recency cue in section header.
- Rationale: Existing backend and contracts already encode recency ordering; explicit UI cue makes ordering logic transparent.
- Alternatives considered:
  - Alphabetical ordering by title: conflicts with a recent-updates use case.
  - Hide sorting semantics: lowers user trust in feed freshness.

## Decision 3: Extend row content to support editorial body copy

- Decision: Ensure each row has fields needed for source/date context, strong title, concise summary line, and geography context when present.
- Rationale: The editorial design requires richer text than the minimal title-only recent card payload.
- Alternatives considered:
  - Derive body copy from title only: too weak for scan comprehension.
  - Fetch row details with per-item follow-up requests: unnecessary latency and complexity for homepage load.

## Decision 4: Row actions are explicit and consistent

- Decision: Each row exposes two consistent actions, View Table and Download CSV, with deterministic destinations.
- Rationale: Consistent actions lower interaction cost and match expected feed utility.
- Alternatives considered:
  - Single action only: reduces usefulness for users who primarily export data.
  - Context menu actions: adds interaction friction for core actions.

## Decision 5: Maintain resilient fallback states

- Decision: Preserve dedicated empty-state and partial-data-safe rendering, without disabling other homepage sections.
- Rationale: Feed availability should not block search or overall homepage usability.
- Alternatives considered:
  - Full-page error on feed payload issues: disproportionate impact for a single section.
  - Silent omission of feed section: poor user feedback and degraded trust.

## Decision 6: Validation strategy remains cross-layer

- Decision: Validate with frontend component/page tests plus backend contract/runtime tests for recent payload behavior.
- Rationale: Editorial feed behavior depends on both rendered hierarchy and backend payload shape consistency.
- Alternatives considered:
  - Frontend-only tests: misses payload regression risks.
  - Manual-only visual validation: insufficient for coverage and quality gate rules.
