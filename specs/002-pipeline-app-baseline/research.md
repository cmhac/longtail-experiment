# Research: Pipeline App Baseline

## Pipeline Project Placement

- Decision: Add the new app at `apps/pipeline` as a first-class Nx project with its own
  `project.json`, `pyproject.toml`, and tests.
- Rationale: This keeps the monorepo app topology consistent (`apps/*`), supports
  affected-only execution, and preserves clear boundaries with backend and frontend.
- Alternatives considered:
  - Place pipeline under `tools/`: rejected because it is a product-facing app boundary,
    not workspace-only tooling.
  - Fold pipeline code into backend: rejected because it obscures ownership and makes
    pipeline-specific quality/runtime policies harder to manage.

## Python Tooling Parity with Backend

- Decision: Reuse backend baseline tooling model for pipeline: uv-managed project,
  ruff lint/format, ty type checks, pytest tests, and coverage threshold >= 90%.
- Rationale: Uniform Python workflows reduce onboarding cost and prevent drift between
  two Python apps in the same workspace.
- Alternatives considered:
  - Different lint/type tools for pipeline: rejected because mixed standards would
    violate repository quality policy.
  - Relaxed coverage for pipeline scaffolding: rejected because constitution coverage
    floor applies to affected scope.

## Dagster Baseline Dependency Scope

- Decision: Include Dagster as a baseline dependency only, with no jobs/sensors/schedules
  implemented in this feature.
- Rationale: The feature intent is setup-only with explicit no-business-logic boundary,
  while still establishing the pipeline as Dagster-oriented for future increments.
- Alternatives considered:
  - Delay adding Dagster package entirely: rejected because the specification explicitly
    frames the app as a Dagster pipeline.
  - Implement sample jobs now: rejected as out of scope for baseline-only setup.

## Affected-Only Quality Execution

- Decision: Register pipeline targets in Nx (`lint`, `format`, `typecheck`, `test`,
  `coverage`) and wire workspace quality orchestration so only impacted projects run.
- Rationale: Preserves current affected-only performance behavior while adding a third
  app.
- Alternatives considered:
  - Run full workspace checks for all pipeline changes: rejected due to slower feedback
    and inconsistency with established baseline model.

## Pipeline-to-Backend Handoff Boundary

- Decision: Define a baseline handoff contract that identifies pipeline as upstream
  producer and backend as downstream serving layer, without implementing actual payloads.
- Rationale: Boundary clarity now reduces integration ambiguity in future feature work.
- Alternatives considered:
  - No handoff contract until implementation: rejected because this delays cross-app
    interface alignment.
  - Direct pipeline-to-frontend baseline: rejected because architecture requires backend
    to remain serving boundary for frontend.

## Three-App Local Stack Extension

- Decision: Extend root Docker Compose baseline to include a pipeline placeholder service
  and health check alongside existing backend and frontend placeholders.
- Rationale: This keeps local-first parity and validates the three-app topology early.
- Alternatives considered:
  - Keep pipeline out of compose until real logic exists: rejected because local-stack
    parity is a constitution requirement for new components.
  - Separate compose files per app: rejected because repository baseline uses a unified
    compose startup path.
