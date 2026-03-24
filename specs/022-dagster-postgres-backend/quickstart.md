# Quickstart: Dagster Metadata Postgres Migration

## Purpose

Use this guide to validate local-stack behavior after migrating Dagster metadata persistence from SQLite to dedicated PostgreSQL.

## Prerequisites

- Repository dependencies installed.
- Local Docker runtime available.
- Working tree on branch 022-dagster-postgres-backend.

## 1. Start or restart local stack

Run the canonical local compose startup flow and ensure services become healthy.

Expected result:

- Canonical output-data database role is reachable.
- Dagster metadata database role is reachable.
- Orchestration services report ready only after metadata DB connectivity is established.

## 2. Verify dual database role readiness

Use local-stack verification checks to confirm both roles are independently available.

Expected result:

- Readiness checks pass for metadata role.
- Readiness checks pass for canonical output-data role.

## 3. Validate fail-fast behavior for metadata misconfiguration

Temporarily introduce invalid metadata DB configuration and launch orchestration startup/run path.

Expected result:

- Runtime fails explicitly with actionable diagnostics.
- No silent fallback to SQLite occurs.
- Restoring valid configuration returns system to healthy operation.

## 4. Validate concurrent run reliability

Execute representative concurrent onboarding workload and monitor terminal run status and metadata queryability.

Expected result:

- No lock-protocol storage failures are observed.
- Run history and event logs remain queryable for completed runs.

## 5. Validate canonical output-data isolation

Perform a metadata-focused reset/troubleshooting action and confirm output-data persistence remains intact unless explicitly reset.

Expected result:

- Metadata and output-data operational boundaries remain independent.

## 6. Run required quality gates

Required before commit or handoff:

1. pnpm exec nx run-many -t test --all
2. pnpm exec nx run-many -t coverage --all

Optional focused checks during implementation:

1. bash tools/quality/local-stack/test-db-readiness.sh
2. bash tools/quality/local-stack/test-compose-stack.sh
3. pnpm run affected:test

## Completion Criteria

- Dagster metadata persistence runs on PostgreSQL in local stack.
- Dual database roles are healthy and independently operable.
- Concurrency validation no longer reproduces SQLite locking-protocol failures.
- Documentation and verification scripts align with new runtime contract.
