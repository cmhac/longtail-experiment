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
