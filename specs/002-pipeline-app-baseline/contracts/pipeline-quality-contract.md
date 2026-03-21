# Contract: Pipeline Quality and Affected Execution

## Purpose

Define mandatory quality interfaces for the new pipeline app and its integration into
workspace-level affected execution.

## Required Pipeline Targets

Pipeline project MUST expose these targets:

- `lint`
- `format`
- `typecheck`
- `test`
- `coverage`

Workspace quality orchestration MUST include pipeline in affected target resolution.

## Tooling Contract

- Pipeline dependency/environment management MUST use uv.
- Pipeline project metadata MUST include `pyproject.toml` and `uv.lock`.
- Linting and formatting MUST use ruff.
- Type checking MUST use ty.
- Testing MUST use pytest.
- Coverage threshold MUST be >= 90% for affected pipeline scope.

## Affected-Only Execution Contract

- Pipeline quality targets MUST be invocable through Nx affected commands.
- Isolated pipeline changes MUST NOT trigger unrelated frontend/backend checks, except
  where shared workspace config intentionally broadens scope.
- Workspace-level validation scripts MUST include pipeline path patterns.

## Prohibited Actions

- Suppressing or bypassing pipeline quality gates without explicit owner approval.
- Introducing implementation-only workaround code to satisfy quality gates.
- Reducing pipeline coverage thresholds below repository minimum policy.
