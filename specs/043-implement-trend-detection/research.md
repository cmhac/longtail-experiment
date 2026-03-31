# Research: End-to-End Trend Detection

## Decision 1: Implement a pure trend analysis library in libs/

- Decision: Build trend analysis as a pure Python library with deterministic outputs and no IO/application orchestration logic.
- Rationale: Keeps algorithm behavior testable and reusable across pipeline contexts; matches clarified requirement for strict separation of concerns.
- Alternatives considered:
  - Embed analysis directly in pipeline services: rejected because it couples algorithm evolution to orchestration details.
  - Execute analysis via remote service: rejected for added operational complexity and local parity friction.

## Decision 2: Use explicit terminal analysis outcomes

- Decision: Return explicit outcomes (`significant_trend`, `no_significant_trend`, `insufficient_data`, `error`) from library analysis calls.
- Rationale: Makes persistence and DAG behavior deterministic and testable; aligns with no-op success handling for selected outcomes.
- Alternatives considered:
  - Return nullable trend object only: rejected due to ambiguity between insufficient data and no trend.
  - Throw exceptions for all non-significant outcomes: rejected because ordinary no-op states are not exceptional failures.

## Decision 3: Trigger trend processing as downstream Dagster asset

- Decision: Trend processing runs as its own downstream asset after fetch/update completion, per updated series.
- Rationale: Preserves ingestion/persistence reliability, enables branch-scoped failure handling, and improves idempotent retry semantics.
- Alternatives considered:
  - Inline trend processing in observation write loop: rejected because failures could contaminate ingestion path and complicate retries.
  - Batch all series in one trend asset run: rejected due to weak isolation and harder partial failure handling.

## Decision 4: Enforce branch-scoped failure and state-based idempotency

- Decision: A trend-asset failure fails only the affected source branch; retries over unchanged persisted observation state must not create new lifecycle rows.
- Rationale: Minimizes blast radius while preserving persistence correctness.
- Alternatives considered:
  - Global run failure on any trend error: rejected as overly disruptive.
  - Run-id idempotency only: rejected because unchanged data could still duplicate lifecycle rows.

## Decision 5: Persist lifecycle transitions and normalize overlapping intervals

- Decision: Persist immutable trend lifecycle transitions and normalize any overlapping intervals before frontend rendering.
- Rationale: Supports historical auditability and guarantees deterministic non-overlapping UI spans.
- Alternatives considered:
  - Mutable current-row-only trend state: rejected because it loses historical continuity.
  - Permit overlaps in UI and rely on layered rendering: rejected because user selected strict no-overlap behavior.

## Decision 6: Backend contracts extend existing discovery surfaces

- Decision: Add trend data to existing recent-updates and dataset-detail discovery responses rather than introducing separate trend-only endpoints.
- Rationale: Preserves existing client integration patterns and avoids parallel contract maintenance.
- Alternatives considered:
  - New dedicated trend endpoints only: rejected because feed/detail views already consume existing discovery surfaces.

## Decision 7: Frontend interaction and accessibility policy

- Decision: Implement desktop hover + touch tap-to-pin tooltip behavior, dual direction encoding (color + pattern/icon), single active tooltip rule, and default detail navigation from feed clicks.
- Rationale: Resolves frontend clarifications with explicit accessibility and interaction consistency.
- Alternatives considered:
  - Color-only encoding: rejected for accessibility gaps.
  - Feed deep-link focus state: rejected by clarification in favor of default detail navigation.

## Decision 8: Stage-level engineering discipline

- Decision: At every stage, enforce repeated red/green TDD loops, repeated `pre-commit run --all-files`, then manual local-stack validation via Docker Compose before advancing.
- Rationale: Matches constitution quality/coverage requirements and user-requested workflow.
- Alternatives considered:
  - Implement-first then test: rejected because it increases rework and risk.
  - Automated-only validation with no manual checks: rejected because integration behaviors require runtime verification.
