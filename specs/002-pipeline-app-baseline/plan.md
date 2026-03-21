# Implementation Plan: Pipeline App Baseline

**Branch**: `002-pipeline-app-baseline` | **Date**: 2026-03-21 | **Spec**: `/Users/hackerc/Projects/longtail-experiment/specs/002-pipeline-app-baseline/spec.md`
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/002-pipeline-app-baseline/spec.md`

## Summary

Add a third Nx app named pipeline as a baseline Dagster-oriented Python project that
matches backend quality/tooling standards, extends affected-only quality execution, and
adds three-app local-stack scaffolding without introducing business logic.

## Technical Context

**Language/Version**: Python 3.12 (pipeline/backend), TypeScript 5.x (frontend), Node.js 22 LTS  
**Primary Dependencies**: Nx workspace tooling, uv, ruff, ty, pytest, dagster (baseline package only), pnpm, Biome, Vitest, PMD CPD  
**Storage**: N/A (scaffolding-only feature; no production persistence design)  
**Testing**: pytest for pipeline/backend, Vitest for frontend, workspace smoke checks for registration/quality/local-stack  
**Target Platform**: Local developer environments on macOS/Linux with Docker Desktop or compatible Docker Engine  
**Project Type**: Nx monorepo extension (new Python pipeline app with baseline-only implementation)  
**Performance Goals**: Three-app placeholder stack reaches healthy status in under 5 minutes; affected-only quality checks remain under 3 minutes for small isolated changes  
**Constraints**: No business logic, no quality suppressions, coverage >= 90% for affected scopes, pipeline setup must mirror backend quality model, backend remains frontend-serving layer  
**Scale/Scope**: One additional project (`apps/pipeline`) plus workspace tooling, docs, and compose updates needed for baseline parity

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Pre-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Pipeline is added as an explicit Nx app boundary with
  dedicated ownership, targets, and docs updates.
- Quality gate enforcement: PASS. Plan requires lint/format/type/test/coverage gates for
  pipeline with no suppression path.
- Test and coverage discipline: PASS. Plan includes pipeline tests and coverage
  enforcement at >= 90% for affected scope.
- Local-first parity: PASS. Plan extends unified compose stack and health checks from two
  to three placeholder services.
- Data integrity and reliability: PASS. Pipeline-to-backend handoff contract is explicit,
  versionable, and documented before product logic implementation.
- Documentation fidelity: PASS. Plan includes AGENTS.md and runbook/onboarding updates for
  new app structure and commands.

- Post-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Project structure and contracts preserve clear boundaries among
  pipeline, backend, and frontend.
- Quality gate enforcement: PASS. Canonical pipeline quality commands and affected-target
  integration are defined in contracts and quickstart.
- Test and coverage discipline: PASS. Verification strategy includes pipeline smoke and
  quality command tests with coverage policy retained.
- Local-first parity: PASS. Compose and health verification are designed for three-app
  baseline startup/shutdown flows.
- Data integrity and reliability: PASS. Handoff contract formalizes baseline producer /
  consumer expectations and traceability requirements.
- Documentation fidelity: PASS. Architecture, onboarding, runbooks, and AGENTS.md are
  identified for same-change updates.

## Project Structure

### Documentation (this feature)

```text
/Users/hackerc/Projects/longtail-experiment/specs/002-pipeline-app-baseline/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── pipeline-quality-contract.md
│   ├── pipeline-backend-handoff-contract.md
│   └── local-stack-three-app-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── backend/
│   ├── src/
│   ├── tests/
│   ├── pyproject.toml
│   ├── uv.lock
│   └── project.json
├── frontend/
│   ├── src/
│   ├── tests/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   └── project.json
└── pipeline/
    ├── src/
    │   └── __init__.py
    ├── tests/
    │   ├── test_smoke.py
    │   ├── test_quality_commands.py
    │   ├── test_container_health.py
    │   └── test_workspace_registration.py
    ├── pyproject.toml
    ├── uv.lock
    └── project.json

tools/
└── quality/
    ├── cpd/
    ├── local-stack/
    ├── pmd/
    ├── verification/
    └── project.json

docker/
└── compose/
    └── stack.env

docs/
├── architecture/
├── onboarding/
└── runbooks/

docker-compose.yml
nx.json
package.json
AGENTS.md
```

**Structure Decision**: Extend the current Nx app topology from two apps to three by
adding `apps/pipeline` with backend-parity Python scaffolding and shared workspace
quality/compose orchestration, while preserving existing backend/frontend boundaries.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Implementation Consistency Notes

- Pipeline app scaffolding mirrors backend quality model via uv, ruff, ty, and pytest.
- Workspace quality and duplication tooling include pipeline-aware affected checks.
- Local stack and documentation updates preserve backend-serving boundary for frontend.
