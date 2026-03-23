# Implementation Plan: Frontend Page Furniture Baseline

**Branch**: `015-scaffold-page-furniture` | **Date**: 2026-03-22 | **Spec**: `specs/015-scaffold-page-furniture/spec.md`
**Input**: Feature specification from `/specs/015-scaffold-page-furniture/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace the placeholder frontend with a minimal, runnable Next.js baseline that renders only page furniture scaffolding and an empty main region. The plan introduces app-shell boundaries, typed local furniture adapters, process-hook stubs for future server bootstrap flows, and validation updates so local startup plus quality gates prove the environment is ready for follow-on feature work.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: TypeScript 5.x (frontend), Node.js 22 LTS workspace runtime  
**Primary Dependencies**: Next.js (App Router baseline), React runtime from Next.js, existing Biome/Vitest/TypeScript toolchain, Nx run-commands targets  
**Storage**: N/A for this scaffold-only feature (no data persistence changes)  
**Testing**: Vitest + @vitest/coverage-v8; contract-style shell rendering checks in frontend test suite  
**Target Platform**: Local-first macOS/Linux developer environments and CI runners
**Project Type**: Nx monorepo frontend web application baseline migration  
**Performance Goals**: root shell route loads without blocking runtime errors in 100% of baseline verification runs; furniture placeholders render within initial page paint for local verification  
**Constraints**: no product/editorial content in main region; no private/internal package requirement; preserve strict quality gates and >=90% coverage expectations for affected scope  
**Scale/Scope**: single root route and app shell scaffold, five furniture slots, three process-hook stubs, docs and tests required for local readiness proof

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include
  cross-layer contract updates for vertical-slice changes?
- Quality gate enforcement: Are lint, format, type-check, and test gates defined with no
  suppression, bypass, or workaround strategy?
- Test and coverage discipline: Does the plan include automated tests needed to maintain
  > = 90% coverage across affected backend/frontend projects?
- Local-first parity: Can the complete impacted flow run locally via unified Docker
  Compose, and are compose/healthcheck updates identified?
- Data integrity and reliability: Are data provenance, schema/contract versioning, and
  trend/alert regression protections explicitly designed?
- Documentation fidelity: Does the plan identify all documentation that MUST be added or
  updated for the proposed code and behavior changes?

- Monorepo cohesion: PASS. Changes remain inside `apps/frontend`, frontend tests, and documentation with no boundary sprawl.
- Quality gate enforcement: PASS. Plan keeps lint/format/typecheck/test/coverage gates as mandatory with no suppression strategy.
- Test and coverage discipline: PASS. Plan includes shell/furniture contract tests and quality target updates to maintain coverage floor.
- Local-first parity: PASS. Plan includes local startup and visual shell verification steps and keeps Docker-compose-aware workflow documentation aligned.
- Data integrity and reliability: PASS. No persistence or analytics logic changes; explicit contract boundaries reduce integration risk for future data flows.
- Documentation fidelity: PASS. Plan includes onboarding/runbook updates describing startup and verification for the new frontend baseline.

## Project Structure

### Documentation (this feature)

```text
specs/015-scaffold-page-furniture/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── frontend-shell-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
apps/
└── frontend/
  ├── project.json
  ├── package.json
  ├── tsconfig.json
  ├── vitest.config.ts
  ├── src/
  │   ├── app/
  │   │   ├── layout.tsx
  │   │   ├── page.tsx
  │   │   └── globals.css
  │   ├── shell/
  │   │   ├── app-shell.tsx
  │   │   └── slots/
  │   ├── furniture/
  │   │   ├── contracts.ts
  │   │   ├── adapters/
  │   │   └── placeholders/
  │   └── server/
  │       └── hooks/
  │           ├── env-bootstrap.ts
  │           ├── data-bootstrap.ts
  │           └── publish-extension.ts
  └── tests/
    ├── shell-contract.test.tsx
    ├── startup-smoke.test.tsx
    └── quality-commands.test.ts

docs/
├── onboarding/
│   └── monorepo-baseline.md
└── runbooks/
  └── local-stack-baseline.md
```

**Structure Decision**: Extend `apps/frontend` in place with a minimal App Router shell and adapter-driven furniture boundaries. Keep all frontend behavior in the existing Nx project and validate through existing frontend quality targets plus updated tests.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Resolve baseline frontend architecture decisions before implementation:

- Router and render boundary choice for minimal shell baseline.
- Furniture adapter contract shape and placeholder replacement strategy.
- Process-hook contract boundaries for env/data/publish lifecycle stubs.
- Local verification and quality-gate strategy that proves runtime readiness without introducing product content.

Output captured in `research.md`.

## Phase 1: Design & Contracts

### Data Model

Define shell composition entities (`FrontendShell`, `FurnitureSlot`, `FurnitureAdapterContract`, `ProcessHookContract`, `VerificationScenario`) and invariants in `data-model.md`.

### Interface Contracts

Define shell and furniture slot contracts in `contracts/frontend-shell-contract.md`, including required slot presence and failure semantics.

### Quickstart

Define local startup, visual verification, and quality-gate validation steps for the frontend baseline in `quickstart.md`.

### Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh codex` after design artifacts are generated.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Documentation fidelity: PASS

## Phase 2: Task Planning Approach

`/speckit.tasks` should generate dependency-ordered tasks across:

1. Frontend runtime migration from placeholder entrypoint to minimal Next.js app shell baseline.
2. App shell + furniture placeholder slot implementation with typed adapter boundaries.
3. Server process hook stubs for environment/data/publish lifecycle extension points.
4. Frontend test updates to validate shell/furniture rendering contracts and startup readiness.
5. Nx/frontend target alignment and documentation updates for startup and verification workflows.

## Implementation Finalization Notes

- Keep primary page content intentionally empty; this feature delivers structure only.
- Ensure furniture placeholders remain visible and stable across desktop and mobile viewport widths.
- Do not couple scaffold runtime to private vendor packages in the initial baseline.
