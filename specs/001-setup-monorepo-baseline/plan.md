# Implementation Plan: Initial Monorepo Baseline

**Branch**: `001-setup-monorepo-baseline` | **Date**: 2026-03-21 | **Spec**: `/specs/001-setup-monorepo-baseline/spec.md`
**Input**: Feature specification from `/specs/001-setup-monorepo-baseline/spec.md`

## Summary

Create an Nx-managed monorepo baseline with barebones backend and frontend projects,
strict quality gates, and a unified local stack run path, while intentionally excluding
all product implementation. The approach standardizes developer setup, codifies quality
policy (lint/format/type/test/coverage), and ensures checks run only for affected
projects.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend), Node.js 22 LTS  
**Primary Dependencies**: Nx workspace tooling, uv, ruff, ty, pytest, pnpm, Vitest,
Biome, TypeScript compiler, PMD CPD  
**Storage**: N/A (no product data storage in baseline scope)  
**Testing**: pytest (backend), Vitest (frontend), baseline smoke checks for workspace and
local stack startup  
**Target Platform**: Local developer environments on macOS/Linux with Docker Desktop or
compatible Docker Engine  
**Project Type**: Nx monorepo full-stack baseline (tooling and scaffolding only)  
**Performance Goals**: Local full-stack placeholder startup reaches healthy state in
under 5 minutes; affected-only quality checks complete in under 3 minutes for small
changes  
**Constraints**: No product/business implementation code; strict no-suppression policy
for quality gates; >= 90% coverage threshold enforced; checks must be scoped by Nx
affected graph; cross-repo duplication detection via `pmd cpd --minimum-tokens 50`  
**Scale/Scope**: One backend project and one frontend project initialized with tooling,
workspace-level quality orchestration, and unified Docker Compose local stack wiring

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Pre-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Nx project boundaries are explicit (`apps/backend`,
  `apps/frontend`, `tools/quality`), and cross-workspace contracts are documented.
- Quality gate enforcement: PASS. Lint, format, type-check, tests, and duplication checks
  are mandatory with no suppression/bypass policy.
- Test and coverage discipline: PASS. Coverage gate is defined at >= 90% per affected
  project scope for backend and frontend.
- Local-first parity: PASS. Unified Docker Compose stack with placeholder health checks
  is part of baseline deliverables.
- Data integrity and reliability: PASS. No production data behavior is introduced; initial
  contracts and validation boundaries are documented for future evolution.

- Post-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Project graph, target naming, and ownership boundaries are
  consistent with Nx and constitution rules.
- Quality gate enforcement: PASS. All required tools and commands are codified in
  workspace-level contracts and quickstart.
- Test and coverage discipline: PASS. Coverage enforcement and test entry points are
  specified for both projects.
- Local-first parity: PASS. Compose startup and health verification flow is specified.
- Data integrity and reliability: PASS. Baseline contract artifacts define startup,
  quality, and future interface governance.

## Project Structure

### Documentation (this feature)

```text
specs/001-setup-monorepo-baseline/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── workspace-quality-contract.md
│   └── local-stack-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── backend/
│   ├── src/
│   │   └── __init__.py
│   ├── tests/
│   │   └── test_smoke.py
│   ├── pyproject.toml
│   └── uv.lock
└── frontend/
  ├── src/
  │   └── main.ts
  ├── tests/
  │   └── smoke.test.ts
  ├── package.json
  ├── tsconfig.json
  └── vitest.config.ts

tools/
└── quality/
  ├── pmd/
  │   └── install-pmd.sh
  └── cpd/
    └── run-cpd.sh

docker/
└── compose/
  └── stack.env

docs/
├── architecture/
├── runbooks/
└── onboarding/

docker-compose.yml
nx.json
pnpm-workspace.yaml
```

**Structure Decision**: Use an Nx monorepo with `apps/backend` and `apps/frontend` as
the only initial runnable projects, centralized quality tooling in `tools/quality`, and
a unified `docker-compose.yml` for local stack parity.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |
