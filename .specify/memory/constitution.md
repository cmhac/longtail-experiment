<!--
Sync Impact Report
- Version change: N/A (template) -> 1.0.0
- Modified principles:
	- Template Principle 1 -> I. Monorepo Full-Stack Cohesion
	- Template Principle 2 -> II. Uniform Quality Gates (Non-Negotiable)
	- Template Principle 3 -> III. Test-Driven Verification and Coverage Floor
	- Template Principle 4 -> IV. Local-First Runtime Parity
	- Template Principle 5 -> V. Long-Tail Data Integrity and Trend Reliability
- Added sections:
	- Architecture and Delivery Constraints
	- Development Workflow and Enforcement
- Removed sections:
	- None
- Templates requiring updates:
	- .specify/templates/plan-template.md: ✅ updated
	- .specify/templates/spec-template.md: ✅ updated
	- .specify/templates/tasks-template.md: ✅ updated
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

### II. Uniform Quality Gates (Non-Negotiable)

Strict linting, formatting, type checking, and test gates MUST be enforced for both
backend and frontend through pre-commit hooks and CI. Rule suppression, rule disabling,
temporary bypasses, and one-off gate workarounds are forbidden unless explicitly
authorized by the repository owner for a specific change.
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
- Pull requests MUST show successful lint, format, type-check, and test results for all
  affected projects.
- Any proposal to relax a quality gate MUST be documented in the PR and explicitly
  approved by the repository owner before implementation.
- Non-standard implementations designed only to satisfy gates without preserving intent
  are disallowed.
- Work items MUST include test updates and, when relevant, Docker Compose integration
  updates.
- Constitution compliance MUST be checked during plan review and before merge.

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
  constitution alignment, including quality gates and local-stack runability.
- This constitution is expected to evolve with the product; refinements that tighten
  standards across backend, frontend, data pipelines, and operations are encouraged.

**Version**: 1.0.0 | **Ratified**: 2026-03-21 | **Last Amended**: 2026-03-21
