# Implementation Plan: Local Development Performance Stabilization

**Branch**: `051-local-dev-performance` | **Date**: 2026-04-08 | **Spec**: `/root/snap/longtail-experiment/specs/051-local-dev-performance/spec.md`
**Input**: Feature specification from `/specs/051-local-dev-performance/spec.md`

## Summary

Improve local dataset detail page responsiveness by eliminating full-catalog work on detail requests, reducing avoidable backend request overhead in local runtime, and preserving existing response behavior and contracts for discovery consumers. The plan keeps endpoint shapes stable while changing retrieval strategy and execution profile to match single-dataset request scope.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x + React 19 + Next.js 15 App Router (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x, Pydantic 2.x contracts, HeroUI 3 (`@heroui/react`), Recharts, Nx + pnpm + uv  
**Storage**: PostgreSQL 16 (discovery and trend persistence tables via `libs/db`)  
**Testing**: pytest contract/integration tests (backend), Vitest + React Testing Library (frontend), monorepo stop gates via Nx and pre-commit  
**Target Platform**: Local Linux development via unified Docker Compose stack and browser runtime  
**Project Type**: Nx monorepo web application (backend API + frontend app + shared DB/runtime libs)  
**Performance Goals**: Meet spec outcomes SC-001 through SC-004, including <=3s load for 95% of sampled local detail page loads and >=60% median improvement versus baseline  
**Constraints**: Preserve existing discovery payload semantics, maintain error behavior, avoid regressions across list/search/source/topic/geography endpoints, maintain constitution quality gates  
**Scale/Scope**: Dataset detail request path across frontend server rendering, frontend proxy/API access, backend query/service/repository flow, and local DB access patterns

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Plan covers `apps/backend`, `apps/frontend`, and shared persistence interactions without breaking boundaries.
- Quality gate enforcement: PASS. No suppression/bypass strategy; lint/format/typecheck/test/coverage gates remain mandatory.
- Full-suite stop rule: PASS. Plan mandates `pnpm exec nx run-many -t test --all` before commit and handoff.
- Coverage stop rule: PASS. Plan mandates `pnpm exec nx run-many -t coverage --all` before commit with >=90% thresholds.
- Test and coverage discipline: PASS. Includes backend contract/integration and frontend behavior tests for the changed path.
- Local-first parity: PASS. Plan explicitly validates in Docker Compose local stack and local browser flow.
- Data integrity and reliability: PASS. No schema contract break; detail payload correctness and trend evidence behavior are preserved.
- Configuration integrity: PASS. No new credentialed services/components are introduced.
- Frontend UI consistency: PASS. No new UI system; existing HeroUI/Tailwind usage remains unchanged.
- Documentation fidelity: PASS. Plan includes research, data-model, contract, and quickstart artifacts.

## Project Structure

### Documentation (this feature)

```text
specs/051-local-dev-performance/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- dataset-detail-performance-contract.md
`-- tasks.md
```

### Source Code (repository root)

```text
apps/backend/
|-- src/http_api_server.py
|-- src/query/
|   |-- dataset_discovery_service.py
|   `-- dataset_discovery_persisted_repository.py
`-- tests/
    |-- contract/
    `-- integration/

apps/frontend/
|-- src/app/datasets/[id]/page.tsx
|-- src/lib/api/discovery-client.ts
`-- tests/

libs/db/
|-- src/db/models/
`-- src/db/repositories/
```

**Structure Decision**: Keep implementation as a vertical performance slice centered on the dataset-detail path; backend repository/service logic changes are primary, with frontend consumption behavior and test coverage updates to confirm unchanged contract behavior and improved perceived load.

**User Story Boundaries**:
- US1 addresses user-visible local detail-page speed (navigation-to-content and loading-state dwell time).
- US2 addresses backend detail request-scope and scaling behavior while preserving contract semantics.
- US3 addresses repeated-request local runtime overhead stability.

## Phase Plan

### Phase 0: Research and Decision Lock

- Quantify the dominant contributors to local detail latency across:
  - detail metadata retrieval strategy,
  - observation/evidence enrichment path,
  - local backend runtime request overhead.
- Lock decisions for:
  - dataset-targeted metadata retrieval approach,
  - as-of descriptor candidate resolution approach that minimizes unnecessary in-memory filtering,
  - local runtime request-overhead reductions that preserve safety and correctness.
- Define baseline/after measurement protocol for SC-001/SC-002/SC-003.
- Output: `research.md` with all decisions and no unresolved clarifications.

### Phase 1: Design and Contracts

- Author `data-model.md` for request-path entities and execution-profile constraints.
- Author `contracts/dataset-detail-performance-contract.md` describing:
  - unchanged detail response shape expectations,
  - endpoint behavior invariants,
  - non-functional latency acceptance targets for local development verification.
- Author `quickstart.md` with local baseline measurement, implementation validation flow, and stop-gate commands.
- Run `.specify/scripts/bash/update-agent-context.sh codex`.

### Phase 2: Implementation Planning

#### Workstream A: Backend dataset detail retrieval scope

1. Replace broad metadata load behavior in detail path with dataset-targeted retrieval.
2. Ensure detail metadata path cost scales with one requested dataset.
3. Preserve payload shape and not-found/error semantics.

#### Workstream B: Backend observation and trend evidence assembly

1. Reduce unnecessary candidate scanning/filtering work in as-of descriptor mapping path.
2. Keep deterministic observation ordering and as-of descriptor correctness.
3. Preserve canonical descriptor and lookback evidence correctness in output.

#### Workstream C: Local runtime request overhead

1. Reduce avoidable per-request setup overhead in local backend service processing.
2. Keep schema readiness and runtime safety checks intact.
3. Validate stability across repeated detail requests.

#### Workstream D: Frontend route and integration verification

1. Keep dataset detail route behavior and error handling unchanged.
2. Validate reduced loading-state dwell time for local detail navigation.
3. Ensure no discovery endpoint regressions from frontend perspective.

#### Workstream E: Validation and quality gates

1. Add/adjust automated tests for dataset detail performance-sensitive code paths and invariants.
2. Record baseline vs after local measurements aligned to SC-001 through SC-004.
3. Execute required quality gates and local runtime verification commands.

## Execution Guidance (Mandatory)

- Use red/green test-first increments for backend detail-path changes.
- Validate local behavior with clean stack restart discipline when testing end-to-end:
  - `docker compose down`
  - `docker compose up -d`
- Before commit or handoff, run and pass:
  - `pre-commit run --all-files`
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

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
