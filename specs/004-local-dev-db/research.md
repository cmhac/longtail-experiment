# Research: Local Development Database Readiness

## Local Database Runtime Topology

- Decision: Add a dedicated local PostgreSQL service to the unified compose stack and keep persistence enabled by default.
- Rationale: Developers need stable data across restarts for migration/debug loops; explicit reset supports clean-state tests without forcing daily rebuilds.
- Alternatives considered:
  - Ephemeral database on every startup: rejected because repeated reseeding slows iteration.
  - External shared database for local work: rejected because it breaks local-first parity and introduces coordination risk.

## Migration Execution Entry Point

- Decision: Use one canonical migration command path tied to shared DB migration assets in `libs/db/alembic`.
- Rationale: A single entry point reduces onboarding confusion and makes migration failures reproducible in CI/local validation.
- Alternatives considered:
  - Multiple app-specific migration commands: rejected because backend/pipeline drift can occur.
  - Manual SQL migration steps: rejected because they are non-repeatable and error-prone.

## Migration Failure Policy

- Decision: Fail fast on first migration error, emit actionable recovery guidance, and require explicit rerun.
- Rationale: Partial forward progress during failure hides root causes and can leave schema state ambiguous.
- Alternatives considered:
  - Continue on error: rejected because downstream errors become harder to diagnose.
  - Auto-reset-and-rerun: rejected because it can destroy expected local state unexpectedly.

## Local/Non-Local Boundary

- Decision: Enforce development-only usage through explicit warnings in docs and command guidance (no runtime hard guard).
- Rationale: Matches clarified spec decision while still reducing accidental misuse through visible operator messaging.
- Alternatives considered:
  - Hard runtime environment guard: rejected to remain aligned with clarification choice.
  - No boundary language: rejected because it increases misuse risk.

## Setup Defect Remediation Scope

- Decision: Treat all reproducible setup and migration defects found during implementation as in-scope fixes.
- Rationale: Partial severity-only remediation leaves onboarding instability unresolved and violates clarified acceptance intent.
- Alternatives considered:
  - Fix blocker/high only: rejected because medium/low defects still create recurring friction.
  - Defer all but blockers: rejected because readiness outcome would be incomplete.

## Verification Command Strategy

- Decision: Local readiness verification must include migration status check, stack-health check, and full affected quality commands.
- Rationale: Setup is only complete when the environment and quality gates are both stable.
- Alternatives considered:
  - Run only migration checks: rejected because regressions can still break lint/type/test pipelines.
  - Run only affected tests: rejected because migration-state correctness can be missed.

## US1 Bootstrap Validation Evidence

- Command: `bash tools/quality/local-stack/test-local-db-bootstrap.sh`
  - Result: PASS after adding bounded health polling for DB readiness.
  - Timing note: DB reached healthy status within the script timeout window (<=30 seconds) on repeated runs.
- Command: `uv run --project apps/backend pytest apps/backend/tests`
  - Result: PASS (24 passed), coverage 94.03%.
- Command: `uv run --project apps/pipeline pytest apps/pipeline/tests`
  - Result: PASS (31 passed), coverage 96.39%.

## US2 Migration Verification Evidence

- Command sequence (single fresh run):
  1. `docker compose down -v`
  2. `docker compose up -d db`
  3. `bash tools/quality/local-stack/run-db-migrations.sh`
  4. `bash tools/quality/local-stack/check-db-revision.sh`
  5. `docker compose down`
  - Result: PASS with `Revision OK: 0001_contract_baseline`.
- Repeated reliability check: 20 fresh-run attempts using the same sequence.
  - Result: 20/20 successful attempts.
  - Computed success rate: 100% (target >=95%).
- Command: `uv run --project apps/backend pytest apps/backend/tests libs/db/tests`
  - Result: PASS (39 passed), coverage 94.03%.

## US3 Defect Verification Evidence

- Defect DB-001 (host port collision):
  - Verification commands:
    1. `bash tools/quality/local-stack/test-local-db-bootstrap.sh`
    2. 20 fresh-run attempts of migration + revision check sequence.
  - Result: PASS; success rate 20/20 (100%), no cross-connection to host PostgreSQL on 5432.
- Defect DB-002 (scripts required manual DB start):
  - Verification commands:
    1. `docker compose down`
    2. `bash tools/quality/local-stack/run-db-migrations.sh`
    3. `bash tools/quality/local-stack/check-db-revision.sh`
  - Result: PASS; scripts auto-started local DB and completed migration/revision checks.

## Phase 6 Validation Evidence

- Quickstart/readiness validation command:
  - `bash tools/quality/local-stack/test-db-readiness.sh`
  - Result: PASS (bootstrap + migration + revision + compose-stack verification successful).
- Full affected quality gate commands:
  - `pnpm run affected:lint`
  - `pnpm run affected:format`
  - `pnpm run affected:typecheck`
  - `pnpm run affected:test`
  - `pnpm run affected:coverage`
  - `pnpm run affected:duplication`
  - Result: PASS across all affected targets.
- Shell script portability/strictness command:
  - `uv run --project apps/backend pytest libs/db/tests/test_local_stack_script_portability.py`
  - Result: PASS (2 passed).
