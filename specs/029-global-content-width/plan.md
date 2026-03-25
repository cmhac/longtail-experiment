# Implementation Plan: Global Page Content Width

**Branch**: `[029-global-content-width]` | **Date**: 2026-03-25 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/029-global-content-width/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/029-global-content-width/spec.md)
**Input**: Feature specification from `/specs/029-global-content-width/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Introduce a single global default max-content-width policy for shell page content so home and datasets listing views remain readable on very wide desktop screens, while preserving intentional full-width surfaces through explicit opt-out behavior.

The implementation focuses on shared shell/page layout behavior and targeted layout regression coverage, without changing data contracts or page workflows.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing shell layout classes, discovery page components, theme tokens, Next.js page composition  
**Storage**: N/A (presentation/layout behavior only)  
**Testing**: Vitest, frontend typecheck, Biome checks, Nx monorepo stop-gate suites  
**Target Platform**: Web application (desktop-first usage with responsive mobile support)
**Project Type**: Frontend web application feature in Nx monorepo  
**Performance Goals**: Maintain current page rendering responsiveness while introducing shared width constraints  
**Constraints**: Keep existing navigation/filter/sort/fallback behavior unchanged; preserve explicit full-width shell surfaces (header/footer bands)  
**Scale/Scope**: Shared default width behavior for shell pages, with explicit exception handling and regression coverage on home and datasets routes

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include
  cross-layer contract updates for vertical-slice changes?
- Quality gate enforcement: Are lint, format, type-check, and test gates defined with no
  suppression, bypass, or workaround strategy?
- Full-suite stop rule: Does the plan require `pnpm exec nx run-many -t test --all` to
  pass before any commit and before any AI agent ends work, with no exceptions?
- Coverage stop rule: Does the plan require `pnpm exec nx run-many -t coverage --all`
  to pass before any commit with >= 90% thresholds for every project?
- Test and coverage discipline: Does the plan include automated tests needed to maintain
  > = 90% coverage across affected backend/frontend projects?
- Local-first parity: Can the complete impacted flow run locally via unified Docker
  Compose, and are compose/healthcheck updates identified?
- Data integrity and reliability: Are data provenance, schema/contract versioning, and
  trend/alert regression protections explicitly designed?
- Configuration integrity: Do all new services/pipeline components fail hard on missing
  env vars/credentials (no soft outcomes), and is `docker/compose/local.secrets.env`
  declared as an `env_file` source for any service that requires secrets?
- Documentation fidelity: Does the plan identify all documentation that MUST be added or
  updated for the proposed code and behavior changes?

- Monorepo cohesion: PASS - feature remains within frontend shell/layout boundaries with no cross-service drift.
- Quality gate enforcement: PASS - no suppression or bypass strategy is required.
- Full-suite stop rule: PASS - required before commit and before agent handoff/end.
- Coverage stop rule: PASS - required before commit with threshold compliance.
- Test and coverage discipline: PASS - plan includes layout behavior checks for default and full-width exception cases.
- Local-first parity: PASS - no new services; behavior is verifiable in existing local frontend runtime.
- Data integrity and reliability: PASS - no data or schema behavior changes.
- Configuration integrity: PASS - no new credentialed service/component behavior.
- Documentation fidelity: PASS - planning artifacts and context docs are updated for this layout policy change.

## Project Structure

### Documentation (this feature)

```text
specs/029-global-content-width/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
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
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx
    │   │   ├── datasets/page.tsx
    │   │   └── globals.css
    │   ├── shell/
    │   │   ├── site-header.tsx
    │   │   └── site-footer.tsx
    │   └── theme/
    │       └── monochrome-theme.ts
    └── tests/
        ├── shell-structure-contract.test.tsx
        ├── home-page.test.tsx
        └── catalog-page.test.tsx
```

**Structure Decision**: Keep implementation fully within apps/frontend shared shell/layout surfaces so default width behavior is centralized and inherited by shell pages.

## Phase 0 Research Outcomes

See /Users/hackerc/Projects/longtail-experiment/specs/029-global-content-width/research.md.

- Choose a single global default width policy applied at shell page content level.
- Preserve full-bleed header/footer shell bands and enable explicit full-width exceptions.
- Validate behavior with layout-focused assertions and manual viewport checks.

## Phase 1 Design Artifacts

- Data model: /Users/hackerc/Projects/longtail-experiment/specs/029-global-content-width/data-model.md
- Interface contract: /Users/hackerc/Projects/longtail-experiment/specs/029-global-content-width/contracts/global-content-width-contract.md
- Quickstart: /Users/hackerc/Projects/longtail-experiment/specs/029-global-content-width/quickstart.md
- Agent context update command: `.specify/scripts/bash/update-agent-context.sh codex`

## Implementation Phases

### Phase 2 Delivery Plan

1. Define shared layout primitives for default constrained content width and explicit full-width opt-out behavior.
2. Apply default constrained behavior to representative shell page content surfaces, including home and datasets routes.
3. Preserve intentional full-width shell regions and document their exception status.
4. Add or update layout regression coverage for constrained defaults and explicit full-width exceptions.
5. Run required frontend checks and mandatory monorepo stop gates before commit/handoff.

## Verification Plan

- Focused checks during implementation:
  - `pnpm --dir apps/frontend test -- tests/shell-structure-contract.test.tsx tests/home-page.test.tsx tests/catalog-page.test.tsx`
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

Post-design constitution re-check: PASS on all gates.

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.
