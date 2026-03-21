# Research: Initial Monorepo Baseline

## Workspace Orchestration

- Decision: Use Nx as the monorepo orchestrator for backend and frontend projects.
- Rationale: Nx provides a project graph and affected-task execution that minimizes check runtime by running only relevant targets for changed files.
- Alternatives considered:
  - Plain npm/pnpm workspaces only: rejected because affected-only task execution and graph-aware orchestration are weaker out of the box.
  - Independent repos: rejected because it conflicts with constitution requirements for monorepo cohesion.

## Backend Toolchain

- Decision: Use uv for Python environment and dependency management with `pyproject.toml` and `uv.lock`; use ruff for lint/format, ty for type checking, and pytest for tests.
- Rationale: This stack aligns with requested standards and supports strict, automatable quality gates in pre-commit and CI.
- Alternatives considered:
  - Poetry/Pipenv: rejected because user explicitly selected uv.
  - mypy/pyright for type checking: rejected because user explicitly selected ty.

## Ruff Lint Policy

- Decision: Enforce the exact lint selector and ignore list in backend `pyproject.toml`.
- Rationale: Exact rule parity is required to prevent drift and avoid ad hoc quality interpretation.
- Alternatives considered:
  - Reduced/expanded rule sets: rejected because this baseline must codify exact policy from requirements.

## Frontend Toolchain

- Decision: Use pnpm as package manager, Vitest for testing, Biome for linting and formatting, and `tsc --noEmit` for type checks with strict mode enabled.
- Rationale: Single toolchain for lint+format reduces config overhead and improves consistency; strict TypeScript enforces early correctness.
- Alternatives considered:
  - ESLint + Prettier: rejected because user explicitly selected Biome.
  - Jest: rejected because user explicitly selected Vitest.

## Cross-Repo Duplication Detection

- Decision: Add a workspace-level duplication gate using PMD CPD with `--minimum-tokens 50` across backend and frontend source paths.
- Rationale: A single cross-repo duplication standard catches copy/paste drift early and applies equally to both stacks.
- Alternatives considered:
  - Language-specific duplicate checkers only: rejected because they do not provide one uniform cross-repo policy.

## PMD Installation Method

- Decision: Codify PMD setup with the provided installation script and pin version 7.22.0.
- Rationale: Version pinning keeps local and CI behavior deterministic.
- Alternatives considered:
  - Homebrew/system packages: rejected because availability and version parity vary by environment.

## Affected-Only Quality Execution

- Decision: Configure Nx targets and named inputs so lint/format/type/test/cpd checks run through affected commands for changed projects only.
- Rationale: This satisfies the requirement to avoid unnecessary full-repo checks while preserving mandatory gates.
- Alternatives considered:
  - Full-repo checks for every commit: rejected due to poor feedback time and unnecessary compute.

## Local Stack Baseline

- Decision: Use one unified Docker Compose file to launch placeholder backend/frontend services and health checks.
- Rationale: This fulfills constitution local-first parity and proves full-stack wiring before implementation features exist.
- Alternatives considered:
  - Separate compose files per project: rejected because it weakens the single-command local stack contract.

## Baseline Scope Verification Evidence

- Product endpoint scan: Placeholder-only backend/frontend modules are present; no domain
  workflow endpoints are introduced in this feature branch.
- Quality pipeline evidence:
  - `pnpm run quality:all` completed successfully on 2026-03-21, including affected
    lint, format, typecheck, test, coverage, and duplication targets.
  - Backend gates passed with 100% coverage (threshold >= 90% satisfied).
  - Frontend gates passed with 100% coverage (threshold >= 90% satisfied).
- Local stack verification evidence:
  - `bash tools/quality/local-stack/test-compose-stack.sh` completed successfully
    on 2026-03-21 after Docker daemon startup.
  - Compose stack started and stopped cleanly with both placeholder services
    present in `docker compose ps` output.
