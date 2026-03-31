# Implementation Plan: End-to-End Trend Detection

**Branch**: `043-implement-trend-detection` | **Date**: 2026-03-31 | **Spec**: `/specs/043-implement-trend-detection/spec.md`
**Input**: Feature specification from `/specs/043-implement-trend-detection/spec.md`

## Summary

Implement trend detection as a vertical slice in four strict implementation stages: (1) trend analysis library, (2) pipeline integration as downstream Dagster asset(s), (3) backend discovery/API integration, and (4) frontend feed/detail integration. The delivery strategy is test-first at every stage using explicit red/green TDD loops, followed by manual validation against the local Docker Compose stack, and repeated pre-commit quality runs throughout implementation.

## Technical Context

**Language/Version**: Python 3.12 (library/backend/pipeline), TypeScript 5.x + React 19 + Next.js 15 (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x, Alembic, Pydantic 2.x, Dagster 1.x, pytest, Ruff, Ty, HeroUI 3, Recharts, Vitest, Biome  
**Storage**: PostgreSQL 16 (`source_profiles`, `data_series`, `observations`, new trend persistence tables via Alembic)  
**Testing**: pytest + pytest-cov (backend/pipeline/libs), Vitest + coverage (frontend), pre-commit, Nx monorepo test/coverage gates  
**Target Platform**: Local Docker Compose stack and Linux container runtime parity  
**Project Type**: Nx monorepo full-stack feature (library + data pipeline + API + web UI)  
**Performance Goals**: Per-series trend asset execution scales with source parallelism without blocking observation persistence; UI remains responsive and readable with trend overlays  
**Constraints**: Preserve deterministic library outputs; trend failures remain dataset/source-branch scoped; maintain >=90% coverage for every project; keep frontend on HeroUI + Tailwind patterns  
**Scale/Scope**: All trend-enabled datasets in discovery catalog; historical + ongoing trend lifecycle support; unified recent feed plus dataset detail chart overlays

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Plan spans `libs`, `apps/pipeline`, `apps/backend`, and `apps/frontend` with contract/data-model artifacts.
- Quality gate enforcement: PASS. No suppression or bypasses; explicit repeated pre-commit checks per stage.
- Full-suite stop rule: PASS. Plan requires `pnpm exec nx run-many -t test --all` before commit/stop.
- Coverage stop rule: PASS. Plan requires `pnpm exec nx run-many -t coverage --all` before commit.
- Test and coverage discipline: PASS. TDD loops and project-specific test additions are mandatory at each stage.
- Local-first parity: PASS. Each stage includes manual Docker Compose validation commands.
- Data integrity and reliability: PASS. Trend lifecycle transitions, idempotency, deterministic outputs, and failure scope are explicit.
- Configuration integrity: PASS. No soft-fail credential policy changes; existing compose env-file conventions remain authoritative.
- Frontend UI consistency: PASS. HeroUI/Tailwind and shared component extraction are required for repeated patterns.
- Documentation fidelity: PASS. Plan updates include spec artifacts, contracts, and quickstart/manual test instructions.

## Project Structure

### Documentation (this feature)

```text
specs/043-implement-trend-detection/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── discovery-trends.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
libs/
├── trend_analysis/
│   ├── src/
│   └── tests/
└── db/
    └── alembic/

apps/pipeline/
├── src/pipeline/orchestration/
├── src/pipeline/services/
└── tests/

apps/backend/
├── src/app/discovery/
├── src/contract/
└── tests/

apps/frontend/
├── src/app/
├── src/components/
├── src/lib/
└── tests/
```

**Structure Decision**: Multi-project vertical slice using existing monorepo boundaries. The trend analysis library is implemented in `libs/` first, then consumed by pipeline, then surfaced by backend and frontend.

## Phase Plan (Ordered Implementation)

### Phase 0: Research and Final Technical Decisions

- Consolidate algorithm and implementation decisions in `research.md`.
- Confirm trend transition signature, deterministic result structure, cadence/seasonality failure semantics, and frontend interaction accessibility rules.
- Capture alternatives considered and rejected.

### Phase 1: Stage-Ordered Implementation Plan

#### Stage 1: Trend Analysis Library (first)

1. Create shared Python library package under `libs/` with pure, side-effect-free analysis functions.
2. Implement deterministic trend output contract (`significant`, `no_significant_trend`, `insufficient_data`, explicit error states).
3. Implement cadence inference + seasonality handling behavior aligned with clarified failure semantics.
4. Enforce hardcoded in-library thresholds/cadence defaults only, with no external runtime configuration overrides.
5. Couple analysis-version identity directly to released library version and validate deterministic repeatability under that version identity.
4. Use these prototype files as implementation and test-guidance references for scenario coverage shape and edge-case sampling:
   - `specs/043-implement-trend-detection/prototype/spike_real_series_seasonality.py`
   - `specs/043-implement-trend-detection/prototype/spike_multi_horizon.py`

Stage 1 quality loop (mandatory, repeated):

- Red: Write failing unit tests first for each rule (signature change detection, no-significant close behavior, insufficient data, cadence failure, deterministic repeatability).
- Green: Implement minimal code to pass.
- Refactor: Tighten APIs and type hints with tests still green.
- Run stage checks repeatedly:
  - `uv run --project apps/backend pytest` (or project-targeted library pytest invocation once library project wiring exists)
  - `uv run --project apps/backend ruff check`
  - `uv run --project apps/backend ty check`
  - `pre-commit run --all-files`

Stage 1 manual validation (mandatory):

- Restart local stack cleanly: `docker compose down && docker compose up -d`
- Run one-off real-data verification command(s) that execute the library against local DB-backed sample series and verify deterministic results across repeated calls.
- If manual checks fail, fix, then rerun red/green tests and manual checks before advancing.

#### Stage 2: Pipeline Integration (second)

1. Add trend processing as dedicated downstream Dagster asset path after fetch/update completion.
2. Ensure per-updated-series execution granularity and branch-scoped failure semantics.
3. Enforce state-based idempotency for lifecycle writes on retries.
4. Implement successful no-op handling for `insufficient_data` and `no_significant_trend` outcomes with explicit metadata.
5. Implement backfill behavior for zero-existing-trend series with sufficient history.
6. Add/extend DB migration(s) and repository paths for trend lifecycle persistence.
7. Implement operator-triggered manual full rerun/full historical re-backfill workflow when a library release changes trend-analysis behavior.

Stage 2 quality loop (mandatory, repeated):

- Red: Add failing orchestration/repository/integration tests first (asset dependency ordering, failure isolation, idempotent retries, no-op outcomes).
- Green: Implement minimal pipeline code + persistence to satisfy tests.
- Refactor: Improve orchestration clarity and metric/log consistency.
- Run stage checks repeatedly:
  - `uv run --project apps/pipeline pytest apps/pipeline/tests`
  - `uv run --project apps/pipeline ruff check apps/pipeline`
  - `uv run --project apps/pipeline ty check apps/pipeline`
  - `pre-commit run --all-files`

Stage 2 manual validation (mandatory):

- Restart local stack cleanly: `docker compose down && docker compose up -d`
- Trigger one-off ingestion/trend execution in local environment and verify:
  - observation persistence succeeds when trend asset fails for one series
  - only affected source branch fails
  - no duplicate lifecycle rows on retry with unchanged observation state
- If any mismatch appears, fix and repeat red/green loop + manual test.

#### Stage 3: Backend Integration (third)

1. Extend discovery contracts and repository/query layer for trend lifecycle and feed items.
2. Add unified recent updates feed behavior with trend items using trend start period ordering.
3. Add dataset detail trend span payload with fields required by frontend behavior (including non-overlap normalization inputs/outputs).
4. Ensure malformed/missing trend payload conditions map to explicit error semantics expected by frontend.
5. Preserve baseline no-trend behavior so discovery responses remain fully usable when trend records are absent.

Stage 3 quality loop (mandatory, repeated):

- Red: Add failing contract and service tests for feed ordering, payload shape, and error behavior.
- Green: Implement minimal query/service/API changes.
- Refactor: Normalize shared mappers/types and keep contract naming consistent.
- Run stage checks repeatedly:
  - `uv run --project apps/backend pytest apps/backend/tests`
  - `uv run --project apps/backend ruff check apps/backend`
  - `uv run --project apps/backend ty check apps/backend`
  - `pre-commit run --all-files`

Stage 3 manual validation (mandatory):

- Restart local stack cleanly: `docker compose down && docker compose up -d`
- Execute one-off API calls (curl/httpie) for recent updates and dataset detail; verify trend event ordering, payload fields, and error-mode behavior.
- Fix any issue found and rerun tests + manual checks.

#### Stage 4: Frontend Integration (fourth)

1. Update unified feed to display trend items interleaved with dataset updates.
2. Remove unused trends tab from top navigation.
3. Add dataset detail trend overlays with:
   - green/up and red/down semantics
   - dual encoding for accessibility (pattern/icon)
   - non-overlapping rendered regions
   - single active tooltip policy
   - desktop hover and touch tap-to-pin interactions
4. Apply navigation behavior: trend feed click opens dataset detail default view (no trend-focused URL state).
5. Enforce explicit error-state rendering when required trend span payload is missing/malformed.
6. Reuse/extract shared components in `apps/frontend/src/components` for repeated trend UI patterns.
7. Preserve baseline no-trend dataset detail/feed usability so absence of trend data does not degrade core interactions.

Stage 4 quality loop (mandatory, repeated):

- Red: Write failing component/page tests first for rendering, interactions, accessibility encoding, and error state.
- Green: Implement minimal UI and view-model changes.
- Refactor: Extract reusable components and eliminate duplicated markup/class patterns.
- Run stage checks repeatedly:
  - `pnpm --dir apps/frontend test`
  - `pnpm --dir apps/frontend exec biome check .`
  - `pnpm --dir apps/frontend typecheck`
  - `pre-commit run --all-files`

Stage 4 manual validation (mandatory):

- Restart local stack cleanly: `docker compose down && docker compose up -d`
- Launch frontend and perform manual browser checks for desktop and touch-sized viewport interactions; validate one-tooltip behavior, non-overlap display, and error state rendering.
- Fix discovered issues and rerun red/green tests and manual checks.

### Phase 2: Cross-Stage Hardening and Release Readiness

1. Verify end-to-end flow from ingestion through pipeline, backend, and frontend.
2. Re-run pre-commit repeatedly until clean after all cross-layer fixes.
3. Run mandatory stop gates before commit/handoff:
   - `pnpm exec nx run-many -t test --all`
   - `pnpm exec nx run-many -t coverage --all`
4. Update any impacted docs and ensure contracts/data model remain aligned with implemented behavior.

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

No constitution violations or exception requests identified.
