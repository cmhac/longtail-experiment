# Research: Real Backend Discovery API Runtime

## Decision 1: Remove runtime fixture composition from startup paths

- Decision: Runtime discovery HTTP startup uses persisted repository composition only, with no fixture-backed startup mode or fallback mode.
- Rationale: This directly enforces FR-001, FR-002, and FR-011 while eliminating the mismatch where ingest succeeded but API remained fixture-backed.
- Alternatives considered:
  - Keep fixture-backed runtime as default with a persisted opt-in toggle.
    - Rejected because it preserves ambiguous behavior and violates the ban on runtime fixture paths.
  - Keep dual runtime modes selected by environment.
    - Rejected because it allows accidental regressions and undermines local/CI trust.

## Decision 2: Restrict fixtures to automated test scope only

- Decision: Fixture datasets remain available only in tests, test factories, and test-specific wiring; runtime modules and compose startup do not consume fixture repositories.
- Rationale: Preserves fast deterministic tests while maintaining production-intent runtime parity.
- Alternatives considered:
  - Remove fixtures from repository entirely.
    - Rejected because tests still benefit from deterministic fixture scenarios.
  - Allow fixtures in local runtime for convenience.
    - Rejected because this is exactly the mismatch the feature is correcting.

## Decision 3: Verify ingest-to-API parity as a hard acceptance path

- Decision: Add at least one integration path that performs ingest (or verifies newly persisted records) and then asserts discovery endpoint response changes from persisted data.
- Rationale: Prevents regressions where ingest and API diverge despite passing isolated tests.
- Alternatives considered:
  - Validate repository calls in isolation only.
    - Rejected because wiring regressions can still hide behind unit tests.
  - Validate API shape only without data delta assertions.
    - Rejected because shape-only checks miss persisted-data parity failures.

## Decision 4: Preserve existing response contracts while swapping data source

- Decision: Keep endpoint shapes and not-found semantics stable; change only runtime data source and verification expectations.
- Rationale: Limits frontend risk and keeps implementation focused on correctness and parity.
- Alternatives considered:
  - Redesign endpoint payloads in the same feature.
    - Rejected because it increases scope and obscures the core runtime correction.
  - Introduce temporary compatibility flags.
    - Rejected because flags can reintroduce forbidden fallback behavior.

## Decision 5: Enforce deterministic ordering from persisted records

- Decision: Continue deterministic ordering for search, recent, catalog, and detail responses with persisted-record tie-breakers.
- Rationale: Deterministic ordering is required for reproducible UI behavior and stable tests.
- Alternatives considered:
  - Database natural order.
    - Rejected due to non-deterministic row order risk.
  - Endpoint-specific ad hoc ordering without shared rules.
    - Rejected due to contract drift risk across discovery surfaces.
