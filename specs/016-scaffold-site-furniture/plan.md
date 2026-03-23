# Implementation Plan: Minimal Site Furniture Shell

**Branch**: `016-scaffold-site-furniture` | **Date**: 2026-03-23 | **Spec**: `specs/016-scaffold-site-furniture/spec.md`
**Input**: Feature specification from `/specs/016-scaffold-site-furniture/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a strict structure-only application shell with header, main placeholder, and footer; enforce an extremely minimal monochromatic visual language with no accent color usage; and support device preference-aware light/dark mode from initial release. The implementation keeps scope constrained to foundational furniture and relies on the existing frontend component system to maximize consistency and reduce custom styling drift.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Node.js 22 LTS workspace runtime  
**Primary Dependencies**: Next.js App Router runtime, React runtime from Next.js, HeroUI component system, existing Biome/Vitest/TypeScript/Nx toolchain  
**Storage**: N/A (UI scaffold only, no persistence changes)  
**Testing**: Vitest + @vitest/coverage-v8, shell contract assertions for structure/theme behavior  
**Target Platform**: Local-first macOS/Linux developer environments and CI runners
**Project Type**: Nx monorepo frontend web application shell refinement  
**Performance Goals**: Root shell renders without blocking runtime errors in 100% of baseline runs; first render consistently includes all shell regions in both theme modes  
**Constraints**: No product content in main placeholder; no accent-color usage in shell UI; preserve strict quality gates and >=90% coverage expectations for affected scope  
**Scale/Scope**: Single app shell composition for root layout plus monochrome light/dark theming behavior and verification updates

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

- Monorepo cohesion: PASS. Changes are limited to existing frontend/runtime docs scopes and do not introduce cross-boundary coupling.
- Quality gate enforcement: PASS. Plan requires lint/format/typecheck/test/coverage checks with no suppression strategy.
- Test and coverage discipline: PASS. Plan includes shell-structure and theme-behavior assertions to maintain affected coverage.
- Local-first parity: PASS. Plan includes local runtime verification in both light and dark preference modes.
- Data integrity and reliability: PASS. No data contracts or analytics pipelines are changed; scope remains presentation-only.
- Documentation fidelity: PASS. Plan includes quickstart/run instructions for shell and theme verification.

## Project Structure

### Documentation (this feature)

```text
specs/016-scaffold-site-furniture/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── shell-theme-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── frontend/
  ├── src/
  │   ├── app/
  │   │   ├── layout.tsx
  │   │   ├── page.tsx
  │   │   └── globals.css
  │   ├── shell/
  │   │   ├── site-header.tsx
  │   │   ├── site-footer.tsx
  │   │   └── content-placeholder.tsx
  │   └── theme/
  │       └── monochrome-theme.ts
  └── tests/
    ├── shell-structure-contract.test.tsx
    └── shell-theme-preference.test.tsx

docs/
└── runbooks/
  └── local-stack-baseline.md
```

**Structure Decision**: Extend the existing frontend application in place and keep scope to shell structure and appearance behavior only. Use existing app layout entry points and keep verification in frontend tests plus runbook updates.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Resolve shell and theme design decisions before implementation:

- HeroUI-first composition approach for header/footer/placeholder scaffolding.
- Monochromatic token and class usage strategy that avoids accent leakage.
- Device preference-aware light/dark behavior and verification approach.
- Minimal responsive shell behavior across mobile and desktop.

Output captured in `research.md`.

## Phase 1: Design & Contracts

### Data Model

Define shell composition and appearance entities (`SiteShell`, `ShellRegion`, `AppearanceMode`, `MonochromeStyleRule`, `VerificationScenario`) and invariants in `data-model.md`.

### Interface Contracts

Define shell-structure and theming behavior expectations in `contracts/shell-theme-contract.md`, including required region presence, monochrome constraints, and device preference mode expectations.

### Quickstart

Define local startup and verification steps for shell structure and theme behavior in `quickstart.md`.

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

1. App shell layout updates for header, footer, and explicit content placeholder.
2. HeroUI-first shell components with monochromatic styling constraints.
3. Device preference-aware light/dark mode behavior in global shell presentation.
4. Frontend tests covering region presence, monochrome constraints, and theme preference behavior.
5. Quickstart and runbook updates for local verification.

## Implementation Finalization Notes

- Keep content scope intentionally structural and avoid product-feature additions.
- Enforce no accent colors in shell-level tokens, classes, and component variants.
- Keep light/dark behavior preference-aware from initial render.
- Implemented shell regions via `site-header.tsx`, `content-placeholder.tsx`, and `site-footer.tsx` with HeroUI `Card` primitives.
- Removed legacy five-slot furniture scaffold modules to keep affected coverage and contracts aligned with the new three-region shell baseline.
