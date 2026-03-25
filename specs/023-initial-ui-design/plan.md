# Implementation Plan: Initial UI Design

**Branch**: `023-initial-ui-design` | **Date**: 2026-03-24 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/023-initial-ui-design/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/023-initial-ui-design/spec.md)
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/023-initial-ui-design/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver the first intentional UI shell slice by replacing the placeholder header with a full-width top navigation bar that includes Longtail serif branding, Home/Datasets/Trends tabs, and right-side search/profile icon controls, while preserving strict scope boundaries through disabled behavior for search/Datasets/Trends and a profile dropdown placeholder.

The implementation will use existing frontend shell composition and HeroUI primitives, establish explicit navbar interaction state definitions, support both light and dark appearance modes, and add contract-focused tests that verify layout semantics and interaction constraints.

## Technical Context

**Language/Version**: TypeScript 5.x with React 19 in Next.js 15 App Router  
**Primary Dependencies**: HeroUI 3 components, Next.js navigation primitives, existing frontend theme tokens  
**Storage**: N/A (presentation and client interaction state only)  
**Testing**: Vitest + React Testing Library style rendering helpers in `apps/frontend/tests` and existing frontend contract/smoke suites  
**Target Platform**: Browser UI rendered by Next.js frontend (desktop and mobile widths)
**Project Type**: Frontend web application feature slice within Nx monorepo  
**Performance Goals**: Navbar and dropdown interactions feel immediate and preserve baseline shell responsiveness; no additional network requests for disabled controls  
**Constraints**: Keep search/Datasets/Trends behavior intentionally disabled; preserve existing discovery page functionality; no suppressions/bypasses for lint/type/test gates  
**Scale/Scope**: Single navbar slice affecting shell/header component, related styling, and frontend tests/documentation

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

- Monorepo cohesion: PASS - scope is isolated to existing frontend shell and test paths without new boundary creation.
- Quality gate enforcement: PASS - delivery requires standard lint/typecheck/test/coverage gates with no bypasses.
- Full-suite stop rule: PASS - completion requires `pnpm exec nx run-many -t test --all` before commit/handoff.
- Coverage stop rule: PASS - completion requires `pnpm exec nx run-many -t coverage --all` before commit.
- Test and coverage discipline: PASS - plan includes explicit contract and interaction tests for navbar behavior and disabled controls.
- Local-first parity: PASS - feature runs in existing local frontend runtime with no compose topology changes.
- Data integrity and reliability: PASS - no data schema changes; UI behavior contract is explicit and testable.
- Configuration integrity: PASS - no new credentials or secret-bearing services introduced.
- Documentation fidelity: PASS - feature docs artifacts and quickstart validation steps are included.

Post-design re-check: PASS on all gates. No constitution violations identified.

## Phase 0 Research Outcomes

See `/Users/hackerc/Projects/longtail-experiment/specs/023-initial-ui-design/research.md`.

- Selected navbar composition using existing shell header ownership and HeroUI controls.
- Selected interaction-state strategy for disabled controls and profile placeholder behavior.
- Selected accessibility and responsive behavior baseline for light/dark support and narrow viewports.

## Phase 1 Design Artifacts

- Data model: `/Users/hackerc/Projects/longtail-experiment/specs/023-initial-ui-design/data-model.md`
- Interface contract: `/Users/hackerc/Projects/longtail-experiment/specs/023-initial-ui-design/contracts/navbar-ui-contract.md`
- Quickstart: `/Users/hackerc/Projects/longtail-experiment/specs/023-initial-ui-design/quickstart.md`
- Agent context update executed via `.specify/scripts/bash/update-agent-context.sh codex`

## Project Structure

### Documentation (this feature)

```text
specs/023-initial-ui-design/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── navbar-ui-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── frontend/
    ├── src/
    │   ├── shell/
    │   │   └── site-header.tsx
    │   ├── app/
    │   │   ├── page.tsx
    │   │   └── globals.css
    │   └── theme/
    │       └── monochrome-theme.ts
    └── tests/
        ├── shell-structure-contract.test.tsx
        └── home-page.test.tsx
```

**Structure Decision**: Keep all implementation in existing frontend shell and test surfaces. No new package/app is needed because the feature is a single UI slice and existing shell boundaries already isolate header responsibilities.

## Implementation Phases

### Phase 2 Delivery Plan

1. Replace placeholder header content with a full-width navbar layout including brand, primary tabs, and utility icon controls.
2. Implement route-safe interaction behavior: brand/Home navigate to home, Datasets/Trends disabled, search icon disabled.
3. Implement profile icon dropdown with only the placeholder text `dropdown coming soon`.
4. Apply/adjust theme-aware styles for light and dark readability, including narrow-viewport layout behavior.
5. Add or update frontend tests to lock structure, disabled interactions, dropdown rendering, and mode/readability expectations.
6. Run required quality gates and full monorepo stop-gate commands.

## Verification Plan

- Focused checks while developing:
  - `pnpm --dir apps/frontend test -- shell-structure-contract.test.tsx`
  - `pnpm --dir apps/frontend test -- home-page.test.tsx`
  - `pnpm --dir apps/frontend typecheck`
  - Manual runtime verification in local dev server for light/dark and narrow viewport behavior
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.

## Post-Implementation Snapshot

- Added a new navbar configuration module at `apps/frontend/src/shell/navbar-config.ts` to define tab and utility control states.
- Replaced placeholder shell header content with a full-width navbar in `apps/frontend/src/shell/site-header.tsx`, including brand/home routing, disabled Datasets/Trends/search controls, and profile dropdown toggle behavior.
- Added shared navbar class tokens in `apps/frontend/src/theme/monochrome-theme.ts` and implemented responsive/light-dark-aware navbar styling in `apps/frontend/src/app/globals.css`.
- Added focused navbar behavior and appearance tests in `apps/frontend/tests/navbar-interactions.test.tsx`, `apps/frontend/tests/navbar-profile-dropdown.test.tsx`, and `apps/frontend/tests/navbar-theme-mode.test.tsx`, and expanded existing shell/home contract assertions.
