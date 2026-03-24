<!--
Sync Impact Report
- Version change: 1.3.0 -> 1.4.0
- Modified principles:
  - None renamed
- Added sections:
  - VII. Configuration Integrity and Credential Safety (new principle)
- Removed sections:
  - None
- Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ updated
  - .specify/templates/spec-template.md: ✅ updated
  - .specify/templates/tasks-template.md: ✅ updated
  - AGENTS.md: ⚠ pending — review for local secrets file convention reference
  - .specify/templates/commands/*.md: ⚠ pending (directory not present)
- Follow-up TODOs:
  - None
-->

# Longtail Experiment Constitution

## Core Principles

### I. Monorepo Full-Stack Cohesion

All backend (Python), frontend (Node.js), shared contracts, and infrastructure artifacts
MUST live in a single Nx-managed monorepo with explicit ownership boundaries and clear
interfaces. Cross-layer changes MUST be delivered as coherent vertical slices with
updated contracts, tests, and documentation in the same change.
Rationale: The product goal depends on tightly coupled ingest, analytics, alerting, and
client delivery; monorepo coordination reduces drift and integration failures.

### II. Uniform Quality Gates and Full-Suite Stop Rule (Non-Negotiable)

Strict linting, formatting, type checking, and test gates MUST be enforced for both
backend and frontend through pre-commit hooks and CI. Rule suppression, rule disabling,
temporary bypasses, and one-off gate workarounds are forbidden unless explicitly
authorized by the repository owner for a specific change.
Before any commit, and before any AI agent stops work or hands off work, the full
repository test suite across all apps MUST pass using the canonical command
`pnpm exec nx run-many -t test --all`. Targeted test runs MAY be used during
development, but they do not satisfy this mandatory stop rule.
Before any commit, repository-wide coverage enforcement MUST pass using
`pnpm exec nx run-many -t coverage --all`, with minimum thresholds of 90% or
higher required for every project.
Rationale: Consistent, automated quality controls are required to keep reliability high
as the codebase and team scale.

### III. Test-Driven Verification and Coverage Floor

Every production change MUST include automated tests at the appropriate level (unit,
integration, and contract/end-to-end where relevant), and the repository-wide minimum
coverage MUST remain at or above 90% for backend and frontend code. Merges that reduce
coverage below 90% are prohibited.
Rationale: Historical analysis and trend alerting require high confidence in correctness
under evolving datasets and rules.

### IV. Local-First Runtime Parity

The full system MUST be runnable locally end-to-end, from data ingest through trend
detection/alerting to the client-facing application, using one unified Docker Compose
stack. New components are not complete until they are integrated into the local stack
with reproducible startup, health checks, and developer-facing run instructions.
Rationale: Local reproducibility is the baseline for developer productivity, integration
safety, and confidence before distributed deployment.

### V. Long-Tail Data Integrity and Trend Reliability

Ingestion, transformation, and trend/alert logic MUST preserve source provenance,
timestamp semantics, and reproducible computation. Data contracts, schema evolution, and
alert thresholds MUST be explicit, versioned, and tested against historical scenarios to
prevent silent regressions.
Rationale: The core product value depends on trustworthy long-horizon analytics and
timely, reliable signal detection.

### VI. Documentation Fidelity and Change Traceability

When new code, interfaces, workflows, commands, or operational behaviors are introduced,
the relevant documentation MUST be created or expanded in the same change. When changes
affect existing behavior, contracts, setup, runbooks, or developer workflows, the
corresponding existing documentation MUST be updated in the same change.
`AGENTS.md` is a mandatory maintained document and MUST be updated regularly to reflect
the current repository structure, active toolchain, and canonical developer commands.
Rationale: The repository must remain understandable and operable as it evolves;
documentation drift causes onboarding friction, operational mistakes, and review blind
spots.

### VII. Configuration Integrity and Credential Safety

All services, pipeline components, and ingest jobs MUST fail fast and hard when required
environment variables or credentials are absent. Silent swallowing of missing-credential
errors — including recording a soft failure outcome in the database while reporting
overall job success — is strictly forbidden. A missing required env var MUST propagate
as an unambiguous hard failure that surfaces visibly to the caller (exception, non-zero
exit, job-level failure in the orchestrator).

The canonical local secrets file is `docker/compose/local.secrets.env`. All Docker
Compose services that require secrets MUST declare it as an `env_file` source so that it
is loaded automatically on every `docker compose up` without any manual invocation.
This file MUST be gitignored. A tracked example template (`local.secrets.env.example`
or equivalent) MUST be maintained alongside it and kept current whenever secrets
requirements change.

No fallback default values are permitted for credentials or external API keys. The
absence of a secret is always a hard error.
Rationale: Silent credential failures produce false-positive job health signals, make
missing configuration invisible until runtime inspection of internal records, and erode
trust in operational monitoring. Fail-fast surfaces the real problem immediately and
unambiguously.

## Architecture and Delivery Constraints

- Repository structure MUST support Nx orchestration across backend, frontend, shared
  contracts/libraries, and infrastructure definitions.
- Backend services MUST use Python with explicit typing and static type checking enabled.
- Frontend applications/libraries MUST use Node.js tooling with static type checking
  enabled where applicable.
- Public interfaces between backend, analytics jobs, and frontend clients MUST be defined
  as versioned contracts.
- Breaking interface or schema changes MUST include migration notes and compatibility
  strategy before merge.
- Observability MUST be implemented for ingest pipelines and alerting paths (structured
  logs at minimum; metrics/tracing introduced as features require).

## Development Workflow and Enforcement

- Every change MUST pass local pre-commit hooks before review.
- Before any commit and before any AI agent ends a work session, the full monorepo test
  suite MUST be executed with `pnpm exec nx run-many -t test --all` and MUST pass.
- Before any commit, monorepo coverage MUST be executed with
  `pnpm exec nx run-many -t coverage --all` and MUST pass with per-project minimums
  of 90% or higher.
- Pull requests MUST show successful lint, format, type-check, and test results for all
  affected projects.
- Any proposal to relax a quality gate MUST be documented in the PR and explicitly
  approved by the repository owner before implementation.
- Non-standard implementations designed only to satisfy gates without preserving intent
  are disallowed.
- Partial, targeted, or affected-only test execution is insufficient for commit or
  agent-stop approval, even when those checks pass.
- Work items MUST include test updates and, when relevant, Docker Compose integration
  updates.
- Work items MUST include documentation impact assessment and required updates before
  merge; documentation omissions for impacted areas are non-compliant, including stale
  or missing updates to AGENTS.md when repository behavior or workflows change.
- Constitution compliance MUST be checked during plan review and before merge.
- Any new service or pipeline component that requires credentials or external API keys
  MUST declare `docker/compose/local.secrets.env` as an `env_file` source in
  `docker-compose.yml` and MUST raise a hard error (not a soft outcome) if those
  variables are absent at runtime.

## Governance

- This constitution is the highest-priority engineering policy for this repository.
  In case of conflict, this document supersedes ad hoc local practices.
- Amendments require: (1) a documented rationale, (2) an explicit impact assessment on
  templates/workflows, and (3) approval from the repository owner.
- Versioning policy for this constitution follows semantic versioning:
  - MAJOR: Incompatible governance changes or principle removals/redefinitions.
  - MINOR: New principle/section or materially expanded guidance.
  - PATCH: Clarifications, wording improvements, or non-semantic edits.
- Compliance review is mandatory for every pull request; reviewers MUST confirm
  constitution alignment, including full-suite test stop-rule compliance,
  commit-time coverage stop-rule compliance, quality gates, local-stack runability,
  configuration integrity (no silent credential failures, secrets file declared),
  and required documentation updates.
- This constitution is expected to evolve with the product; refinements that tighten
  standards across backend, frontend, data pipelines, and operations are encouraged.

**Version**: 1.4.0 | **Ratified**: 2026-03-21 | **Last Amended**: 2026-03-23
