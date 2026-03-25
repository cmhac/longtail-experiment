# Implementation Plan: Unified Dataset List Item

**Branch**: `[028-unify-dataset-list-item]` | **Date**: 2026-03-25 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/028-unify-dataset-list-item/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/028-unify-dataset-list-item/spec.md)
**Input**: Feature specification from `/specs/028-unify-dataset-list-item/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver one reusable dataset row component shared by homepage recent updates and datasets listing views, using the homepage editorial row layout as the visual baseline while preserving existing page behaviors (home feed fallback semantics and datasets filter/sort controls).

The implementation is frontend-focused and centered on shared presentation composition, row interaction parity, and regression-safe replacement of the current datasets-page card variant.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing discovery UI components, Next.js routing/link primitives, shell theme tokens, existing discovery API client/types  
**Storage**: N/A (presentation-level unification over existing fetched payloads)  
**Testing**: Vitest, frontend typecheck, Biome checks, Nx monorepo stop-gate suites  
**Target Platform**: Web application (desktop + mobile responsive)
**Project Type**: Frontend web application feature in Nx monorepo  
**Performance Goals**: Maintain current interactive browsing responsiveness for both home feed and datasets list updates  
**Constraints**: Preserve existing page-level functionality and fallback behavior while replacing only row presentation composition; keep datasets filter/sort control styling out of scope  
**Scale/Scope**: Two page surfaces (`/` recent updates and `/datasets` listing) plus shared discovery component/test/style updates

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

- Monorepo cohesion: PASS - feature is a coherent frontend slice inside existing app boundaries.
- Quality gate enforcement: PASS - no suppression or bypass is introduced.
- Full-suite stop rule: PASS - required before commit/handoff.
- Coverage stop rule: PASS - required before commit.
- Test and coverage discipline: PASS - plan includes row contract and behavior regressions across both pages.
- Local-first parity: PASS - no new services; behavior verifiable in existing local frontend runtime.
- Data integrity and reliability: PASS - no schema or contract mutation; payload semantics preserved.
- Configuration integrity: PASS - no new credentialed services/components.
- Documentation fidelity: PASS - feature docs and run validations will be updated in-spec.

## Project Structure

### Documentation (this feature)

```text
specs/028-unify-dataset-list-item/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx
    │   │   └── datasets/page.tsx
    │   ├── components/discovery/
    │   │   ├── RecentUpdatesFeed.tsx
    │   │   ├── DatasetCatalogList.tsx
    │   │   ├── DatasetCard.tsx
    │   │   └── [new shared row component]
    │   ├── lib/api/discovery-types.ts
    │   └── app/globals.css
    └── tests/
        ├── RecentUpdatesFeed.test.tsx
        ├── DatasetCatalogList.test.tsx
        ├── DatasetCard.test.tsx
        ├── datasets-page.test.tsx
        ├── catalog-page.test.tsx
        └── home-page.test.tsx
```

**Structure Decision**: Keep implementation inside `apps/frontend` and replace duplicated row presentation with one shared discovery component consumed by both home feed and datasets list surfaces.

## Phase 0 Research Outcomes

See /Users/hackerc/Projects/longtail-experiment/specs/028-unify-dataset-list-item/research.md.

- Standardize on homepage editorial row layout as the shared visual baseline.
- Preserve page-specific interaction semantics while sharing row presentation logic.
- Keep datasets filter/sort control styling untouched in this feature.

## Phase 1 Design Artifacts

- Data model: /Users/hackerc/Projects/longtail-experiment/specs/028-unify-dataset-list-item/data-model.md
- Interface contract: /Users/hackerc/Projects/longtail-experiment/specs/028-unify-dataset-list-item/contracts/unified-dataset-row-contract.md
- Quickstart: /Users/hackerc/Projects/longtail-experiment/specs/028-unify-dataset-list-item/quickstart.md
- Agent context update command: `.specify/scripts/bash/update-agent-context.sh codex`

## Implementation Phases

### Phase 2 Delivery Plan

1. Create a shared dataset row component based on the current homepage recent-updates layout contract.
2. Refactor homepage recent updates to consume the shared row component while preserving row-wide link behavior and existing fallback states.
3. Refactor datasets listing rows to consume the same shared row component while preserving datasets-page filtering, sorting, and list state transitions.
4. Align metadata normalization across both contexts (source/date/title/summary/tag rendering and missing-data handling).
5. Update styles to remove duplicated row/card divergence and keep responsive readability.
6. Add/update tests covering shared row rendering contract and page-level regression expectations.
7. Run mandatory monorepo stop gates before commit/handoff.

## Verification Plan

- Focused checks during implementation:
  - `pnpm --dir apps/frontend test -- tests/RecentUpdatesFeed.test.tsx tests/datasets-page.test.tsx tests/catalog-page.test.tsx tests/home-page.test.tsx`
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

Post-design constitution re-check: PASS on all gates.

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.
