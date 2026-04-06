# Implementation Plan: Mobile Sidebar Navigation Drawer

**Branch**: `049-mobile-sidebar-drawer` | **Date**: 2026-04-06 | **Spec**: `/root/snap/longtail-experiment/specs/049-mobile-sidebar-drawer/spec.md`
**Input**: Feature specification from `/specs/049-mobile-sidebar-drawer/spec.md`

## Summary

Replace the current cluttered multi-row small-screen top navigation pattern with a right-side hamburger-triggered drawer that covers about 90% of viewport width, preserves existing navigation destinations and utility behaviors (notifications, comparison count, account, sign-out), and conditionally shows admin navigation for admin/owner users. Deliver this as a frontend-focused vertical slice centered on shared shell/header behavior, with responsive styling, role-aware rendering, and explicit auth-guard behavior for protected actions.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 + Next.js 15 App Router  
**Primary Dependencies**: `@heroui/react`, Tailwind CSS v4 utilities, existing shell theme classes, existing auth/session and notification/comparison client utilities  
**Storage**: Browser-local comparison state + existing auth session persistence (no new persistence introduced)  
**Testing**: Vitest + Testing Library component/shell tests in `apps/frontend/tests`, plus repository mandatory gates (`pre-commit run --all-files`, `pnpm exec nx run-many -t test --all`, `pnpm exec nx run-many -t coverage --all`)  
**Target Platform**: Web browsers in small-screen phone and small-tablet viewports; desktop behavior unchanged  
**Project Type**: Nx monorepo frontend web-application slice (`apps/frontend`) with shared shell components  
**Performance Goals**: Drawer open/close state transition begins within 100ms of user input in manual validation, and destination taps complete drawer-close + navigation without visible UI freeze in normal local runtime checks  
**Constraints**: Drawer activation range is <=1024px viewport width and remains disabled above 1024px; drawer width about 90% viewport; background blur + non-interactive backdrop while open; ordered rows fixed by spec; auth-protected taps from signed-out state redirect to `/login`; sign-out routes to `/`  
**Scale/Scope**: Shared shell pages using `SiteHeader`; desktop navbar layout and non-mobile shell behavior remain unchanged

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Work stays within `apps/frontend` shared shell and tests, preserving existing Nx project boundaries.
- Quality gate enforcement: PASS. Plan includes lint/format/type-check/test workflows with no suppression strategy.
- Full-suite stop rule: PASS. Plan requires `pnpm exec nx run-many -t test --all` before commit and before handoff.
- Coverage stop rule: PASS. Plan requires `pnpm exec nx run-many -t coverage --all` before commit with >=90% thresholds.
- Test and coverage discipline: PASS. Plan includes component, behavior, and contract-style test updates for new mobile drawer behavior and auth/role paths.
- Local-first parity: PASS. Frontend behavior remains runnable in existing local stack and frontend dev server flow; no new services required.
- Data integrity and reliability: PASS. No schema change; preserves existing notification/comparison/auth source-of-truth semantics.
- Configuration integrity: PASS. No new credentials or env vars introduced.
- Frontend UI consistency: PASS. Implementation uses HeroUI + Tailwind + shared shell abstractions; no ad hoc feature-local styling files.
- Documentation fidelity: PASS. Plan outputs include research/design/quickstart/contracts artifacts and agent-context refresh.

## Project Structure

### Documentation (this feature)

```text
specs/049-mobile-sidebar-drawer/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- mobile-sidebar-drawer-contract.md
`-- tasks.md
```

### Source Code (repository root)

```text
apps/frontend/
|-- src/shell/
|   |-- site-header.tsx
|   `-- navbar-config.ts
|-- src/components/
|   `-- shell/
|       |-- MobileNavDrawer.tsx
|       `-- MobileNavDrawerAction.tsx
|-- src/app/
|   `-- globals.css
`-- tests/
    |-- navbar-interactions.test.tsx
    |-- shell-structure-contract.test.tsx
    |-- mobile-nav-drawer.test.tsx
    `-- mobile-nav-drawer-auth.test.tsx
```

**Structure Decision**: Implement as a frontend-only change centered on `SiteHeader` composition. Extract repeated drawer primitives to shared shell components under `apps/frontend/src/components/shell` and keep responsive behavior in existing global shell CSS contracts.

## Phase Plan

### Phase 0: Research and Decision Locking

- Confirm existing small-screen navbar behavior and breakpoint contract currently defined in shell/global styling.
- Confirm existing header utilities and source-of-truth integrations:
  - notification bell + unread badge/dropdown behavior
  - comparison counter source and update events
  - auth session loading, role visibility, and sign-out flow.
- Lock mobile drawer UX decisions already clarified in spec:
  - drawer activation range (<=1024px)
  - right-side tray width about 90%
  - destination tap closes drawer immediately
  - sign-out redirects home
  - signed-out protected actions redirect login.
- Decide reusable component boundaries for drawer rows vs utility/footer actions.
- Output: `research.md` with all planning decisions and alternatives.

### Phase 1: Design and Contracts

- Produce `data-model.md` describing UI state model, menu item contracts, role-based visibility, and interaction transitions.
- Produce `contracts/mobile-sidebar-drawer-contract.md` documenting the UI behavior contract (row ordering, visibility rules, redirect behaviors, and shell integration markers).
- Produce `quickstart.md` with local verification flow for mobile drawer behavior across signed-in, signed-out, and admin/non-admin contexts.
- Run agent context refresh script for Codex:
  - `.specify/scripts/bash/update-agent-context.sh codex`

### Phase 2: Implementation Planning

#### Workstream A: Shared shell drawer composition

1. Add mobile drawer trigger control to `SiteHeader` while preserving desktop utility controls.
2. Introduce shared drawer components for ordered menu rows and bottom utility/footer region.
3. Wire drawer open/close state, backdrop behavior, and immediate-close-on-navigation handling.

#### Workstream B: Navigation/auth/role behavior

1. Route drawer rows to required destinations in exact spec order.
2. Reuse comparison counter source and notifications entry behavior in drawer top section.
3. Enforce role-based admin action visibility.
4. Enforce signed-out protected-action redirect behavior to `/login`.
5. Reuse sign-out behavior with redirect to `/`.

#### Workstream C: Responsive styling and interaction contract

1. Update shell responsive styles to replace current multi-row top-nav behavior with drawer trigger in drawer activation range (<=1024px).
2. Implement right-side tray width (~90%), blurred visible background sliver, and non-interactive backdrop semantics.
3. Preserve existing desktop layout and ordering contract.

#### Workstream D: Automated verification

1. Add targeted drawer behavior tests for:
   - row order and presence
   - open/close interactions
   - close-on-navigation
   - signed-out protected redirect
   - admin visibility conditions.
2. Update existing shell/navbar tests as needed for changed mobile interaction model while preserving desktop contract expectations.

#### Workstream E: Quality gates and documentation

1. Validate with frontend-focused checks during development (`pnpm --dir apps/frontend test`, `pnpm --dir apps/frontend typecheck`, `pnpm --dir apps/frontend exec biome check .`).
2. Run required repository gates before handoff/commit:
   - `pre-commit run --all-files`
   - `pnpm exec nx run-many -t test --all`
   - `pnpm exec nx run-many -t coverage --all`
3. Keep spec artifacts and plan docs aligned if scope details evolve.

## Execution Guidance (Mandatory)

- Use existing `SiteHeader` state and utility integrations as source-of-truth; do not duplicate notification/comparison/auth logic.
- Keep all repeated drawer UI patterns in shared components under `apps/frontend/src/components`.
- Preserve existing shell class/test-id contracts unless explicitly updated in tests and contract docs.
- Validate mobile behavior at multiple small-screen sizes within the drawer activation range (<=1024px).

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Full-suite stop rule: PASS
- Coverage stop rule: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Configuration integrity: PASS
- Frontend UI consistency: PASS
- Documentation fidelity: PASS

## Complexity Tracking

No constitution violations requiring justification.
