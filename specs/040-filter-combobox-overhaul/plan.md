# Implementation Plan: Filter Combobox Overhaul

**Branch**: `[040-filter-combobox-overhaul]` | **Date**: 2026-03-30 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/040-filter-combobox-overhaul/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/040-filter-combobox-overhaul/spec.md)
**Input**: Feature specification from `/specs/040-filter-combobox-overhaul/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Restore trustworthy dataset-list filtering by fixing the cross-layer source/category/sort flow, then repair the in-box combobox narrowing behavior, and finally correct dark-mode hover contrast plus active-state styling. The implementation will stay within the existing backend discovery query path and frontend dataset-list control surface, with verification anchored by the current browser-observed regressions. Work must be delivered in small vertical slices with separate commits after each stable checkpoint; the feature must not be implemented as one large commit.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing backend discovery query/service/repository layers, frontend discovery client/types, HeroUI combobox primitives, shared discovery components, Next.js App Router routing state  
**Storage**: PostgreSQL 16 discovery metadata tables already backing dataset catalog responses  
**Testing**: pytest backend contract/runtime tests, Vitest frontend page/component tests, browser-based manual validation, Nx and pre-commit quality gates  
**Target Platform**: Local Docker Compose stack and Next.js-rendered dataset discovery web UI in desktop and mobile browsers  
**Project Type**: Nx monorepo web application (backend service + frontend application vertical slice)  
**Performance Goals**: Preserve immediate-feeling filter interactions while ensuring visible dataset results and combobox option narrowing respond within one interaction cycle  
**Constraints**: No filter or sort regression; preserve >=90% coverage; preserve HeroUI/Tailwind-first frontend patterns; no rule suppression or quality-gate bypass; commit in incremental slices instead of a single large commit  
**Scale/Scope**: Dataset list filter flow across backend catalog query handling, frontend dataset controls/page wiring, contract artifacts, and associated tests/manual validation

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS - Plan keeps changes within existing `apps/backend` and `apps/frontend` discovery boundaries and updates contract artifacts in the same feature slice.
- Quality gate enforcement: PASS - Plan preserves lint/format/typecheck/test enforcement and forbids suppression or workaround-only strategies.
- Full-suite stop rule: PASS - Plan requires `pnpm exec nx run-many -t test --all` before every implementation commit and before agent handoff/stop.
- Coverage stop rule: PASS - Plan requires `pnpm exec nx run-many -t coverage --all` before every implementation commit with >=90% thresholds for every project.
- Test and coverage discipline: PASS - Plan adds backend and frontend automated regression coverage for filter correctness, combobox narrowing behavior, and visual-state expectations.
- Local-first parity: PASS - Impacted flow remains runnable in existing unified Docker Compose and frontend local runtime; no new service is required.
- Data integrity and reliability: PASS - Plan explicitly preserves current catalog contract semantics and adds regression checks to prevent stale or mismatched result scopes.
- Configuration integrity: PASS - No new credentialed services/components are introduced.
- Frontend UI consistency: PASS - Plan stays within HeroUI combobox usage, Tailwind utilities, and existing shared discovery components; no bespoke local CSS is planned beyond shared token-level adjustment if needed.
- Documentation fidelity: PASS - Plan includes updated planning artifacts, UI contract documentation, and quickstart/manual verification guidance.

## Project Structure

### Documentation (this feature)

```text
specs/040-filter-combobox-overhaul/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dataset-filter-overhaul-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── backend/
│   ├── src/
│   │   ├── contract/query/
│   │   ├── query/
│   │   └── http_api_server.py
│   └── tests/contract/
└── frontend/
    ├── src/
    │   ├── app/datasets/
    │   ├── components/discovery/
    │   └── lib/api/
    └── tests/
```

**Structure Decision**: Keep the feature inside the existing discovery backend and dataset-list frontend modules so filter semantics, UI behavior, and regression tests can be updated as one coordinated vertical slice.

## Phase Plan

### Phase 0: Research and Failure Analysis

- Confirm the exact failure point for source/category/sort so URL changes, backend query params, and rendered rows can be traced end to end.
- Confirm HeroUI combobox narrowing expectations for the current component usage pattern and determine what state wiring is missing.
- Confirm the intended dark-mode option hover and active-state border treatment within existing theme tokens and shared discovery styling patterns.
- Record the incremental-commit execution rule for implementation:
  - one commit after backend/frontend filter correctness is stable
  - one commit after combobox option narrowing is stable
  - one commit after UI-state polish and regression hardening is stable

### Phase 1: Design and Contracts

- Define the dataset filter state model that must stay aligned across URL params, backend catalog query handling, and rendered rows.
- Define the combobox option narrowing state model, including typed text, narrowed option subset, clear reset behavior, and no-match behavior.
- Define the UI contract for dark-mode hover readability and thicker active border treatment.
- Complete artifacts: `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.

### Phase 2: Implementation Planning

- Backend correctness workstream:
  - Trace and fix catalog request parsing, service normalization, repository filtering, and aggregation/result alignment as needed so selected source/category/sort actually affect returned rows.
  - Add backend contract/runtime tests that prove filter and sort combinations affect returned datasets correctly.
- Frontend filter-state workstream:
  - Align dataset list page fetches, URL state, request wiring, and rendered rows with the corrected backend behavior.
  - Add frontend tests that prove source/category/sort selections change visible rows and clear stale results.
- Combobox interaction workstream:
  - Wire combobox input state so typing narrows visible options and clearing restores the full list.
  - Add tests for match, no-match, reset, and option-selection flows.
- UI polish workstream:
  - Correct dark-mode hover text contrast and replace the current active highlight treatment with increased border width.
  - Add visual-state assertions where practical and manual dark-mode checks in quickstart.
- Delivery discipline:
  - Commit each completed workstream separately after local targeted verification plus the mandatory full-suite stop-gate commands.
  - Do not defer all work into a single end-of-feature commit.

## Implementation Notes and Sequencing Checkpoints

- Start with the source/category/sort correctness bug because combobox polish is low value until the returned dataset list is trustworthy.
- Reproduce and lock the failing behavior in tests before changing query wiring so later UI work cannot mask unresolved backend/frontend mismatches.
- Keep combobox narrowing work separate from server-side filter correctness to make regressions attributable and commit history readable.
- Apply dark-mode hover and active-border tweaks only after behavior is stable so visual changes do not obscure functional verification.
- After each checkpoint below:
  - run targeted tests for the changed slice
  - perform the relevant manual browser verification
  - run `pre-commit run --all-files`
  - run `pnpm exec nx run-many -t test --all`
  - run `pnpm exec nx run-many -t coverage --all`
  - create a focused commit before moving to the next checkpoint

### Checkpoint A - Filter Correctness

- Source selection changes the returned dataset set.
- Category selection changes the returned dataset set.
- Sort selection changes visible ordering.
- URL state, backend query handling, and rendered rows stay aligned.

### Checkpoint B - Combobox Narrowing

- Typing inside each combobox narrows visible options.
- No-match state is explicit.
- Clearing typed text restores the full option set.
- Selecting from a narrowed list applies the expected filter.

### Checkpoint C - Dark-Mode And Active-State Polish

- Hovered options remain legible in dark mode.
- Active combobox state uses a thicker border instead of the current highlight treatment.
- Focus, pointer, and keyboard interaction states remain coherent.

### Checkpoint D - Final Regression Hardening

- Backend and frontend regression suites pass.
- Manual browser validation confirms all three controls behave correctly.
- Full monorepo tests, coverage, and all-files pre-commit checks pass before final handoff.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS - Design remains within existing backend/frontend discovery modules with synchronized contract and test updates.
- Quality gates and stop rules: PASS - Plan requires all canonical gate commands before each commit, not just at feature end.
- Coverage discipline: PASS - Design adds backend/frontend tests to protect against regressions while preserving >=90% coverage.
- Local-first parity: PASS - No new runtime surfaces are introduced; current compose-backed local stack remains the verification baseline.
- Data integrity/reliability: PASS - Query/result alignment and stale-row prevention are explicit design invariants.
- Configuration integrity: PASS - No new configuration or secrets behavior is introduced.
- Frontend UI consistency: PASS - Design remains HeroUI-first, Tailwind-first, and shared-component-oriented.
- Documentation fidelity: PASS - Planning artifacts, contract notes, quickstart guidance, and commit-discipline instructions are captured in this feature’s docs.

## Complexity Tracking

No constitution violations requiring justification.

## Execution Log

- 2026-03-30 Checkpoint A complete: backend/frontend filter-state normalization and stale-row reset implemented; targeted backend/frontend regression tests added and passing.
- 2026-03-30 Checkpoint B complete: combobox typed narrowing, explicit no-match states, and selection parity implemented with interaction tests.
- 2026-03-30 Checkpoint C complete: dark-mode hover readability and thicker active border treatment implemented with UI-state assertions.
- 2026-03-30 Checkpoint D complete: manual compose-backed API verification plus full quality gates (`pre-commit run --all-files`, `pnpm exec nx run-many -t test --all`, `pnpm exec nx run-many -t coverage --all`) passing.
