# Contract: Dataset Detail Performance Stabilization

## Contract Type

Behavioral and non-functional contract for existing dataset detail and related discovery endpoints during local development optimization.

## In-Scope Endpoints

- Dataset detail read endpoint (dataset-specific detail payload)
- Dataset as-of detail trend resolution path used by detail views
- Related discovery endpoints used for regression checks:
  - catalog
  - search
  - sources
  - topics
  - geographies

## Behavioral Compatibility Requirements

1. Dataset detail response shape remains compatible with current consumers.
2. Existing not-found and validation error behavior remains unchanged.
3. Canonical descriptor and lookback evidence semantics remain unchanged.
4. Observation ordering semantics remain unchanged.
5. No new required fields are introduced for existing consumers.

## Performance Acceptance Requirements (Local Development)

1. Detail path processing is dataset-scoped for detail metadata retrieval.
2. Detail request execution avoids broad full-catalog retrieval work for single-dataset requests.
3. Repeated detail requests avoid avoidable per-request setup overhead accumulation.
4. Measured local outcomes satisfy spec success criteria SC-001 through SC-003.

## Regression Safety Requirements

1. Catalog/search/source/topic/geography endpoint behavior remains functionally consistent.
2. Error-rate outcomes do not regress for detail and related discovery endpoints (SC-004).
3. Existing contract tests for detail and adjacent endpoints continue to pass.

## Verification Evidence

- Baseline and post-change measurement log for dataset detail page loads.
- Automated test results covering detail contract and adjacent endpoint regression.
- Local runtime verification notes from unified Docker Compose environment.
