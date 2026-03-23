# Research: Dataset Discovery Backend API

## Decision 1: Split discovery into dedicated read surfaces

- Decision: Define four distinct read surfaces for landing search, recent updates, full catalog, and dataset detail.
- Rationale: Each user flow has different response shape and ordering needs; separate surfaces reduce coupling and simplify test coverage.
- Alternatives considered:
  - Single monolithic discovery endpoint with mode flags.
    - Rejected because it increases conditional complexity and weakens contract clarity.
  - Frontend composition from multiple low-level primitive queries.
    - Rejected because it pushes backend ordering/filtering semantics into clients.

## Decision 2: Use normalized multi-field matching plus additive DB indexing

- Decision: Implement matching across title, description, geographic scope, and tags with normalized text search semantics, and add supporting indexes/migration changes where current schema is insufficient.
- Rationale: FR-001 and FR-012 require broad matching and acceptable responsiveness; additive indexing is the lowest-risk way to improve query plans while preserving current data model.
- Alternatives considered:
  - Restrict search to dataset title only.
    - Rejected because it fails feature requirements for metadata and tag discovery.
  - Application-side filtering after broad table scans.
    - Rejected because it does not scale and creates unstable latency.

## Decision 3: Derive dataset recency from canonical observation timestamps

- Decision: Recent updates ranking uses latest observation/report timestamp per dataset with deterministic tie-breakers.
- Rationale: Observations are the canonical signal of dataset freshness and align with existing provenance/timestamp semantics.
- Alternatives considered:
  - Sort by dataset creation timestamp.
    - Rejected because it does not represent ongoing dataset updates.
  - Sort by ingestion run metadata alone.
    - Rejected because run timing can diverge from underlying dataset observation recency.

## Decision 4: Enforce deterministic pagination and ordering contracts

- Decision: Search and catalog responses include explicit pagination inputs/outputs and deterministic ordering rules when recency or titles tie.
- Rationale: Stable ordering is required by FR-009 and prevents duplicate/missing cards between page transitions.
- Alternatives considered:
  - Rely on database default ordering.
    - Rejected because row-order nondeterminism creates inconsistent frontend rendering.
  - Cursor-only pagination without deterministic secondary sort.
    - Rejected because equal-key rows still require stable ordering guarantees.

## Decision 5: Return metadata and chronological observations via one detail workflow

- Decision: Detail retrieval returns one metadata object plus chronologically ordered observation points, with optional range constraints that can reduce payload size when requested.
- Rationale: Frontend detail view and chart rendering require both metadata and ordered points; one workflow simplifies client orchestration.
- Alternatives considered:
  - Separate metadata and observation endpoints only.
    - Rejected because it adds extra client round-trips for the primary detail experience.
  - Return reverse-chronological points by default.
    - Rejected because chart rendering and trend interpretation are simpler with chronological order.

## Decision 6: Add explicit not-found and empty-data semantics

- Decision: Unknown dataset identifiers return a clear not-found response; known datasets without observations return metadata with an empty observation list.
- Rationale: This separates identity errors from data-availability states and satisfies FR-011 plus edge-case handling.
- Alternatives considered:
  - Treat missing observations as not-found.
    - Rejected because dataset identity may be valid even when observations are absent.
  - Return generic server errors for unknown identifiers.
    - Rejected because it obscures client behavior and hinders debugging.
