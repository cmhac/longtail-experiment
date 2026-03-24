# Implementation Plan: Dagster Metadata Postgres Migration

**Branch**: `022-dagster-postgres-backend` | **Date**: 2026-03-24 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/022-dagster-postgres-backend/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/022-dagster-postgres-backend/spec.md)
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/022-dagster-postgres-backend/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace Dagster's local default SQLite metadata persistence with a dedicated PostgreSQL-backed metadata database to eliminate lock-protocol failures during concurrent run/event writes.

The implementation will introduce a second database role in the local compose stack, wire Dagster runtime configuration to that role, add startup/readiness and fail-fast behavior for metadata connectivity, and update local runbooks/verification scripts so developers can validate concurrency stability and troubleshoot metadata vs output-data stores independently.

## Technical Context

**Language/Version**: Python 3.12 (pipeline runtime), YAML/shell compose configuration, SQL for database provisioning checks  
**Primary Dependencies**: Dagster orchestration runtime, SQLAlchemy-backed Dagster storage configuration, Docker Compose local stack, PostgreSQL 16 containers  
**Storage**: Two local PostgreSQL database roles: orchestration metadata store and canonical output-data store  
**Testing**: pytest (pipeline and local-stack verification scripts), compose integration checks, targeted runtime validation plus required monorepo stop-gate suites  
**Target Platform**: Local developer environments (macOS/Linux) running unified Docker Compose stack
**Project Type**: Monorepo infrastructure/runtime configuration enhancement with documentation and verification updates  
**Performance Goals**: No SQLite lock-protocol failures during representative concurrent onboarding workload; maintain current local startup and run query responsiveness  
**Constraints**: Preserve existing canonical dataset behavior; fail hard on misconfiguration; satisfy constitution quality and coverage stop rules; keep local-first reproducibility  
**Scale/Scope**: One feature slice spanning compose config, Dagster runtime configuration, verification automation, and runbook/onboarding documentation

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include
  cross-layer contract updates for vertical-slice changes?
- Quality gate enforcement: Are lint, format, type-check, and test gates defined with no
  suppression, bypass, or workaround strategy?
- Full-suite stop rule: Does the plan require `pnpm exec nx run-many -t test --all` to
  pass before any commit and before any AI agent ends work, with no exceptions?
- Coverage stop rule: Does the plan require `pnpm exec nx run-many -t coverage --all`
  to pass before any commit with >= 90% thresholds for every project?
- Test and coverage discipline: Does the plan include automated tests needed to maintain
  > = 90% coverage across affected backend/frontend projects?
- Local-first parity: Can the complete impacted flow run locally via unified Docker
  Compose, and are compose/healthcheck updates identified?
- Data integrity and reliability: Are data provenance, schema/contract versioning, and
  trend/alert regression protections explicitly designed?
- Configuration integrity: Do all new services/pipeline components fail hard on missing
  env vars/credentials (no soft outcomes), and is `docker/compose/local.secrets.env`
  declared as an `env_file` source for any service that requires secrets?
- Documentation fidelity: Does the plan identify all documentation that MUST be added or
  updated for the proposed code and behavior changes?

- Monorepo cohesion: PASS - changes remain in existing stack surfaces (`docker-compose.yml`, compose env/config, pipeline orchestration config, docs/runbooks, verification scripts) without introducing new project boundary drift.
- Quality gate enforcement: PASS - plan requires lint/format/typecheck/test/coverage with no suppression or bypass strategy.
- Full-suite stop rule: PASS - delivery requires `pnpm exec nx run-many -t test --all` before commit or agent handoff.
- Coverage stop rule: PASS - delivery requires `pnpm exec nx run-many -t coverage --all` before commit.
- Test and coverage discipline: PASS - includes integration/verification tests for metadata DB connectivity, dual-store startup checks, and concurrent run persistence behavior.
- Local-first parity: PASS - feature is explicitly local-stack focused with compose/service readiness updates.
- Data integrity and reliability: PASS - plan separates orchestration metadata persistence from canonical output data and defines verification to prevent cross-store regressions.
- Configuration integrity: PASS - orchestration metadata DB settings must fail hard when invalid or absent; no soft-success behavior permitted.
- Documentation fidelity: PASS - plan includes runbook and onboarding updates for dual-database local operation and migration from legacy SQLite metadata.

Post-design re-check: PASS on all gates. No constitution violations identified.

## Phase 0 Research Outcomes

See `/Users/hackerc/Projects/longtail-experiment/specs/022-dagster-postgres-backend/research.md`.

- Selected metadata persistence strategy for Dagster local runtime using PostgreSQL-backed run/event/schedule storage.
- Selected dual-role local database topology and startup/readiness approach in Docker Compose.
- Selected migration/compatibility approach for existing local SQLite metadata users.

## Phase 1 Design Artifacts

- Data model: `/Users/hackerc/Projects/longtail-experiment/specs/022-dagster-postgres-backend/data-model.md`
- Interface contract: `/Users/hackerc/Projects/longtail-experiment/specs/022-dagster-postgres-backend/contracts/dagster-metadata-runtime.md`
- Quickstart: `/Users/hackerc/Projects/longtail-experiment/specs/022-dagster-postgres-backend/quickstart.md`
- Agent context update executed via `.specify/scripts/bash/update-agent-context.sh codex`

## Project Structure

### Documentation (this feature)

```text
specs/022-dagster-postgres-backend/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dagster-metadata-runtime.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── pipeline/
│   ├── src/
│   │   └── orchestration/
│   │       └── ... (Dagster instance/storage config surfaces)
│   └── tests/
│       └── ... (orchestration/storage integration validation)
└── backend/
    └── tests/
        └── ... (if API/runtime contract checks require updates)

docker/
└── compose/
    ├── stack.env
    ├── local.secrets.env.example
    └── ... (local stack scripts and readiness checks)

docs/
└── runbooks/
    └── local-stack-baseline.md

tools/
└── quality/
    └── local-stack/
        └── ... (compose and DB verification scripts)

docker-compose.yml
AGENTS.md
```

**Structure Decision**: Use existing monorepo runtime/configuration and runbook surfaces without creating new apps or libraries. Keep orchestration metadata DB concerns in pipeline/compose/verification paths and preserve backend canonical data responsibilities.

## Implementation Phases

### Phase 2 Delivery Plan

1. Add local-stack configuration for a dedicated Dagster metadata PostgreSQL database role alongside the canonical output data database.
2. Update Dagster runtime/instance configuration to use PostgreSQL-backed run/event/schedule persistence.
3. Add startup/readiness dependencies so orchestration services only proceed when metadata DB is reachable.
4. Add explicit failure behavior for missing/invalid metadata DB configuration.
5. Update local-stack verification scripts to validate dual database availability and metadata-store readiness.
6. Add/adjust orchestration validation tests to prove concurrent run metadata persistence no longer fails with SQLite locking behavior.
7. Update local runbooks and AGENTS guidance for dual-store operation and SQLite-to-Postgres migration expectations.
8. Execute required quality and stop-gate commands.

## Verification Plan

- Focused checks while developing:
  - local compose DB readiness checks for both metadata and output-data roles
  - Dagster run launch and run-log query smoke checks against PostgreSQL metadata backend
  - concurrent run persistence validation scripts
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.

## Post-Implementation Snapshot

- Added a dedicated `dagster_db` PostgreSQL service to local compose and wired Dagit metadata storage env vars separately from canonical output DB vars.
- Added local runtime fail-fast metadata configuration guards for Dagit startup/probe helpers and orchestration definitions enforcement mode.
- Added orchestration/local-stack tests covering metadata storage config, fail-fast diagnostics, dual-role readiness wiring, and script portability.
