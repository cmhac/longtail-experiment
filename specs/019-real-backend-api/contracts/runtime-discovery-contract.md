# Contract: Runtime Discovery Data Sourcing

## Purpose

Define runtime behavior guarantees for backend discovery endpoints so responses are sourced from persisted records, while allowing fixture usage only in automated tests.

## Scope

- Runtime startup behavior for discovery API service composition.
- Discovery endpoint data-source guarantees for search, recent, catalog, and detail surfaces.
- Test-only fixture allowance boundaries.
- Verification contract for ingest-to-API parity.

## Runtime Data Source Guarantees

1. Runtime startup MUST compose discovery services using persisted repositories.
2. Runtime startup MUST NOT compose discovery services using fixture-backed repositories.
3. Runtime fallback paths MUST NOT switch discovery endpoints to fixture-backed data.
4. Fixture-backed repositories MAY be used only in automated test contexts.
5. Test fixture usage MUST NOT be reachable from default local stack startup.

## Endpoint Behavior Constraints

### Search Datasets

- Path: /api/datasets/search
- Guarantee: Results are derived from persisted dataset metadata/tags and persisted recency fields.

### Recent Dataset Updates

- Path: /api/datasets/recent
- Guarantee: Ranking is derived from persisted recency values with deterministic ordering.

### Catalog Datasets

- Path: /api/datasets
- Guarantee: Listing/grouping/filtering use persisted metadata and source relations.

### Dataset Detail

- Path: /api/datasets/{dataset_id}
- Guarantee: Metadata and observations are derived from persisted records; observation ordering is chronological and deterministic.
- Unknown dataset behavior: explicit not-found behavior remains unchanged.

## Test-Only Fixture Contract

Fixtures are allowed only when all of the following are true:

- Execution context is automated test execution.
- Fixture wiring is declared within test-specific setup/factory paths.
- No runtime startup entrypoint references fixture wiring.

Violation condition:

- Any runtime startup, runtime fallback, or local stack default path that can return fixture-backed discovery data is non-compliant.

## Verification Contract

A compliant verification run provides evidence of all items below:

1. Baseline discovery response captured before ingest update.
2. Ingest run persists new or changed canonical records.
3. Post-ingest discovery response changes to reflect persisted records.
4. Runtime fixture path usage count is zero.

## Non-Goals

- Redesigning endpoint payload shapes.
- Introducing new mutation endpoints.
- Changing authentication/authorization behavior.
