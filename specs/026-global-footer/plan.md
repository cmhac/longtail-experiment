# Implementation Plan: Global Footer Component

**Branch**: `[026-global-footer]` | **Date**: 2026-03-25 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/026-global-footer/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/026-global-footer/spec.md)
**Input**: Feature specification from `/specs/026-global-footer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Introduce a screenshot-inspired global footer component for all shell-rendered pages, centered on strong Longtail brand identity and concise mission copy in a minimalist editorial layout.

Implementation reuses existing shell footer composition to preserve consistency, with focused frontend shell/component/style/test updates and no backend or database changes.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing shell components, HeroUI-aligned theme tokens, Next.js routing primitives  
**Storage**: N/A (presentation-only shell/footer content)  
**Testing**: Vitest frontend tests, Biome lint/format, TypeScript typecheck, Nx monorepo gates  
**Target Platform**: Web application (desktop + mobile responsive views)
**Project Type**: Frontend web-app shell enhancement in Nx monorepo  
**Performance Goals**: Preserve existing shell render responsiveness with no perceptible added load delay for footer content  
**Constraints**: Maintain existing shell navigation behavior; preserve light/dark readability; no backend contract changes required  
**Scale/Scope**: One shared global footer component update plus shell/page tests and style adjustments

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

- Monorepo cohesion: PASS - scope is isolated to frontend shell vertical slice with synchronized spec/plan artifacts.
- Quality gate enforcement: PASS - no suppression/bypass strategy introduced.
- Full-suite stop rule: PASS - `pnpm exec nx run-many -t test --all` required before commit/handoff.
- Coverage stop rule: PASS - `pnpm exec nx run-many -t coverage --all` required before commit.
- Test and coverage discipline: PASS - includes shell and page-level automated coverage updates.
- Local-first parity: PASS - feature runs in existing local frontend runtime and compose-backed stack.
- Data integrity and reliability: PASS - no data contract or persistence behavior changes.
- Configuration integrity: PASS - no new credential-dependent services.
- Documentation fidelity: PASS - spec/plan/research/data-model/contracts/quickstart created for this feature.

## Project Structure

### Documentation (this feature)

```text
specs/026-global-footer/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── footer-shell-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── frontend/
    ├── src/
    │   ├── app/
    │   │   └── globals.css
    │   └── shell/
    │       ├── site-footer.tsx
    │       └── shell-regions.ts
    └── tests/
        ├── home-page.test.tsx
        ├── shell-structure-contract.test.tsx
        └── startup-smoke.test.tsx
```

**Structure Decision**: Reuse existing frontend shell composition (`site-footer` within shared shell regions) and update accompanying shell/page tests to enforce global-footer behavior.

## Phase 0 Research Outcomes

See /Users/hackerc/Projects/longtail-experiment/specs/026-global-footer/research.md.

- Reuse existing shell footer region instead of introducing duplicate footer containers.
- Preserve minimalist editorial content shape with brand + mission statement only.
- Validate through frontend shell/page contract tests and theme/viewport checks.

## Phase 1 Design Artifacts

- Data model: /Users/hackerc/Projects/longtail-experiment/specs/026-global-footer/data-model.md
- Interface contract: /Users/hackerc/Projects/longtail-experiment/specs/026-global-footer/contracts/footer-shell-contract.md
- Quickstart: /Users/hackerc/Projects/longtail-experiment/specs/026-global-footer/quickstart.md
- Agent context update command: `.specify/scripts/bash/update-agent-context.sh codex`

## Implementation Phases

### Phase 2 Delivery Plan

1. Update shared footer shell content and structure to match the screenshot-inspired editorial hierarchy.
2. Apply full-width footer styling and readable content padding consistent with existing shell visual language.
3. Ensure light/dark mode legibility and responsive text wrapping on mobile viewports.
4. Verify footer appears on all shell-rendered pages without per-page duplication.
5. Add/adjust shell structure and page-level tests for footer presence, content, and hierarchy.
6. Run mandatory monorepo test and coverage stop gates before commit/handoff.

## Verification Plan

- Focused checks during development:
  - `pnpm --dir apps/frontend lint`
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend test -- tests/shell-structure-contract.test.tsx tests/home-page.test.tsx`
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.
