# Research: Dagster Metadata Postgres Migration

## Decision 1: Metadata backend target for local orchestration

- Decision: Use a dedicated PostgreSQL-backed Dagster metadata store (run, event log, schedule/sensor state) for local development.
- Rationale: Eliminates SQLite file-lock bottlenecks under concurrent writes and aligns with the concurrency profile of provider onboarding runs.
- Alternatives considered:
  - Keep SQLite and reduce run concurrency: reduces throughput and fails the reliability goal for onboarding workloads.
  - Keep SQLite with tuning-only adjustments: still constrained by file-level locking behavior under parallel metadata writes.

## Decision 2: Local database topology

- Decision: Maintain separate database roles in local stack: one for canonical output data and one for orchestration metadata.
- Rationale: Preserves clear operational boundaries, lowers accidental cross-impact during resets/debugging, and supports independent health verification.
- Alternatives considered:
  - Share one database role for both concerns: increases blast radius and blurs ownership boundaries.
  - Add external managed metadata store for local dev: unnecessary complexity for local-first workflow.

## Decision 3: Startup and readiness sequencing

- Decision: Gate orchestration startup/readiness on successful metadata database connectivity checks.
- Rationale: Prevents partial startup states where UI/processes appear healthy but metadata writes fail later.
- Alternatives considered:
  - Best-effort startup with deferred failures: leads to delayed discovery and confusing runtime errors.
  - Manual post-start health checks only: too error-prone and inconsistent across developers.

## Decision 4: Misconfiguration handling contract

- Decision: Missing or invalid metadata DB configuration must fail hard with explicit diagnostics.
- Rationale: Aligns with constitution fail-fast policy and prevents false-success orchestration behavior.
- Alternatives considered:
  - Silent fallback to SQLite: reintroduces the root locking issue and hides misconfiguration.
  - Soft error recording while allowing run continuation: violates configuration integrity requirements.

## Decision 5: Legacy SQLite local migration approach

- Decision: Treat existing local SQLite metadata as legacy local state, provide explicit migration/reset guidance, and avoid automatic in-place migration assumptions.
- Rationale: Local metadata often has low durability requirements; explicit handling avoids unsafe automated conversion logic.
- Alternatives considered:
  - Mandatory automated metadata migration: high complexity, low user benefit for local-only state.
  - Ignore legacy artifacts entirely: risks user confusion and troubleshooting delays.

## Decision 6: Validation strategy for completion

- Decision: Require dual-store readiness verification plus repeated concurrent run validation proving absence of lock-protocol failures.
- Rationale: Demonstrates that the migration solves the observed failure mode while preserving local stack usability.
- Alternatives considered:
  - Configuration-only validation: insufficient to prove runtime reliability under concurrency.
  - Single-run smoke test only: does not exercise contention behavior that triggered the issue.

## Implementation Evidence (2026-03-24)

- Verified metadata-storage configuration tests and Dagit fail-fast diagnostics in pipeline orchestration test suite.
- Verified local-stack script portability checks include dual-role bootstrap enforcement.
- Regenerated pipeline dependency lockfile with `dagster-postgres` resolved for runtime storage backend support.
