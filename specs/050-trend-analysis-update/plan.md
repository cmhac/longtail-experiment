# Implementation Plan: Trend Analysis Upgrade

**Branch**: `050-trend-analysis-update` | **Date**: 2026-04-07 | **Spec**: `/root/snap/longtail-experiment/specs/050-trend-analysis-update/spec.md`
**Input**: Feature specification from `/specs/050-trend-analysis-update/spec.md`

## Summary

Upgrade trend evidence quality while preserving existing multi-stage trend architecture by introducing robust full-window per-lookback scoring, explicit `flat` canonical semantics via versioned contracts, numeric confidence fields, cadence-aware seasonal adjustment, and additive change-point metadata. Implementation uses selected recent tools: `scipy.stats.theilslopes`, `scipy.stats.kendalltau`, `pandas.Series.ewm`, `statsmodels` STL/MSTL and OLS diagnostics, and `ruptures` for limited tie-break/context metadata.

## Technical Context

**Language/Version**: Python 3.12 (libs/pipeline/backend), TypeScript 5.x + React 19 + Next.js 15 App Router (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x, Alembic, Pydantic 2.x, Dagster 1.x runtime orchestration, SciPy, pandas, statsmodels, ruptures, HeroUI 3 (`@heroui/react`), Recharts, pytest, Ruff, Ty, Vitest, Biome  
**Storage**: PostgreSQL 16 via shared `libs/db` migration/model authority (`trend_*`, `observations`, notification/event tables)  
**Testing**: pytest (libs/backend/pipeline), Vitest (frontend), contract tests for discovery payloads, plus monorepo gates `pre-commit run --all-files`, `pnpm exec nx run-many -t test --all`, `pnpm exec nx run-many -t coverage --all`  
**Target Platform**: Linux local development via unified Docker Compose stack + browser frontend runtime  
**Project Type**: Nx monorepo full-stack vertical slice (library + pipeline + backend APIs + frontend consumption)  
**Performance Goals**: Reduce short-horizon direction-flip churn by >=30% (SC-001), reduce false-positive reversal notifications by >=25% (SC-004), maintain reproducible as-of outputs and idempotent event behavior  
**Constraints**: Hard cutover to versioned canonical contract (no dual compatibility), rejection precedence for irregular cadence, no frontend client-side trend inference, detail/as-of include evidence payload while summary remains canonical-only, no outdated statistical packages  
**Scale/Scope**: All eligible datasets and configured lookbacks in discovery trend flow; full contract propagation across libs, pipeline, backend, and frontend

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Plan spans `libs/trend_analysis`, `libs/db`, `apps/pipeline`, `apps/backend`, and `apps/frontend` with versioned contract updates.
- Quality gate enforcement: PASS. No bypass/suppression strategy; normal lint/format/typecheck/test/coverage gates are required.
- Full-suite stop rule: PASS. `pnpm exec nx run-many -t test --all` required before commit and before handoff.
- Coverage stop rule: PASS. `pnpm exec nx run-many -t coverage --all` required before commit with >=90% thresholds.
- Test and coverage discipline: PASS. Plan includes unit/integration/contract tests across compute, persistence, API, and frontend normalization/rendering.
- Local-first parity: PASS. Plan explicitly validates with clean `docker compose down` + `docker compose up -d` restart and real runtime checks.
- Data integrity and reliability: PASS. Versioned contract, explicit rejection semantics, deterministic as-of ordering, and idempotent transition behavior are planned.
- Configuration integrity: PASS. No new credentialed external services introduced; existing fail-fast credential policy remains unchanged.
- Frontend UI consistency: PASS. Frontend changes keep HeroUI/Tailwind and existing shared component patterns.
- Documentation fidelity: PASS. Plan includes research/data-model/contracts/quickstart artifacts and update-agent-context step.

## Project Structure

### Documentation (this feature)

```text
specs/050-trend-analysis-update/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- discovery-trend-v2.openapi.yaml
|-- research/
|   |-- chosen_tools.md
|   `-- library_tool_decisions.md
`-- tasks.md
```

### Source Code (repository root)

```text
libs/trend_analysis/
|-- src/trend_analysis/
|   |-- scoring.py
|   |-- preprocessing.py
|   |-- seasonal_adjustment.py
|   `-- arbitration.py
`-- tests/

libs/db/
|-- alembic/versions/
|-- src/db/models/trends.py
|-- src/db/repositories/
|   |-- interfaces.py
|   `-- postgres_trend_repository.py
`-- tests/

apps/pipeline/
|-- src/orchestration/jobs/trend_runtime_processor.py
|-- src/orchestration/jobs/trend_lifecycle_service.py
|-- src/orchestration/resources/postgres_trend_repository.py
`-- tests/orchestration/

apps/backend/
|-- src/contract/query/
|-- src/query/
|   `-- trend_notification_service.py
|-- src/http_api_server.py
`-- tests/

apps/frontend/
|-- src/lib/api/
|-- src/components/discovery/
|-- src/app/datasets/[id]/
|-- src/app/search/
`-- tests/
```

**Structure Decision**: Deliver as a full-stack vertical change where statistical computation upgrades are implemented in shared Python trend-analysis/runtime layers, persisted through shared DB contracts, exposed by backend APIs with versioned payload semantics, and consumed by frontend canonical/evidence rendering paths without altering primary chip-first UX.

## Phase Plan

### Phase 0: Research and Tooling Decision Lock

- Confirm and codify selected tools and recency policy from feature research:
  - Theil-Sen: `scipy.stats.theilslopes`.
  - Monotonic evidence: `scipy.stats.kendalltau`.
  - Default smoothing: `pandas.Series.ewm`.
  - Seasonal adjustment: `statsmodels.tsa.seasonal.STL` (monthly/weekly), `statsmodels.tsa.seasonal.MSTL` (regular sub-daily).
  - Change-point metadata: `ruptures`.
  - OLS diagnostics: `statsmodels` OLS.
- Lock exclusion of outdated tools (`pymannkendall`, `mannkendall`, `kats`) per recency policy.
- Resolve remaining technical choices for numeric confidence scale, preprocessing metadata fields, and tie-break thresholds.
- Output: `research.md` with no unresolved clarifications.

### Phase 1: Design and Contracts

- Author `data-model.md` with versioned trend descriptor entities, per-lookback evidence payload, and rejection-state precedence.
- Author `contracts/discovery-trend-v2.openapi.yaml` defining:
  - canonical `flat` support,
  - numeric confidence fields replacing categorical strength,
  - OLS diagnostics and evidence payload visibility rules (detail/as-of only),
  - unavailable descriptor shape for irregular-cadence rejection.
- Author `quickstart.md` with TDD-first implementation order and local runtime verification.
- Run `.specify/scripts/bash/update-agent-context.sh codex`.

### Phase 2: Implementation Planning

#### Workstream A: Statistical preprocessing and scoring (`libs/trend_analysis`)

1. Implement EWMA default smoothing with explicit metadata (`method`, parameters, warmup/missing counts).
2. Implement per-lookback Theil-Sen slope scoring with CI outputs.
3. Add monotonic evidence modifier using Kendall tau and p-value transformation.
4. Compute OLS diagnostic context with explicit supplementary-only role.
5. Define numeric confidence/intensity scale and bounded arbitration inputs.

#### Workstream B: Cadence-aware seasonal adjustment

1. Apply STL for monthly/weekly regular cadence where reliability checks pass.
2. Apply MSTL for eligible regular sub-daily series (complete/pre-imputed, multi-season capable).
3. Enforce explicit fallback to non-seasonally-adjusted scoring when checks fail.
4. Keep daily series on non-seasonally-adjusted path in this phase.

#### Workstream C: Canonical arbitration and rejection precedence

1. Preserve full lookback applicability recording for configured catalog.
2. Implement weighted horizon preference: medium primary, short corroborative, long contextual/tie-break.
3. Add explicit canonical `flat` support and numeric `confidence_score` output on a 0.00-1.00 scale.
4. Enforce irregular-cadence hard rejection precedence with unavailable descriptor and reason code.
5. Integrate `ruptures` metadata as limited tie-break/context only, with tie-break activation when absolute confidence gap between top-two candidates is <= 0.05.

#### Workstream D: Persistence and pipeline propagation (`libs/db`, `apps/pipeline`)

1. Version canonical descriptor and lookback snapshot persistence fields (direction enum updates, numeric confidence, OLS diagnostics, evidence metadata, descriptor state/reason semantics).
2. Maintain deterministic as-of ordering and historical snapshot reproducibility.
3. Ensure event generation stays directional-only (`up <-> down`) and excludes transitions involving `flat`.
4. Preserve idempotent replay/backfill behavior with visibility semantics.

#### Workstream E: Backend and frontend contract propagation

1. Update backend query contracts and validators to versioned descriptor/evidence schema.
2. Keep summary/list endpoints canonical-only; expose evidence/OLS only on detail and as-of endpoints.
3. Update frontend API types/normalizers and trend indicator/evidence UI:
   - primary chip remains canonical-only,
   - `flat` and unavailable states supported,
   - OLS/evidence shown only in secondary expandable sections.
4. Update notification copy formatting to direction-first with optional `confidence_score` detail only when `confidence_score >= 0.70`.

#### Workstream F: Verification and rollout safety

1. Add benchmark/backtest harness checks for SC-001 through SC-006.
2. Add contract conformance tests for SC-008/SC-009.
3. Validate UX consistency for SC-010 across list/detail/notifications.
4. Execute and verify fresh-start local data reset posture for prototype cutover, including post-reset validation that legacy rows are absent and only post-reset event/notification rows exist.

## Tool Usage Requirements (Implementation Rules)

- `scipy.stats.theilslopes` MUST be used as primary per-lookback trend slope estimator.
- `scipy.stats.kendalltau` MUST be used as monotonic evidence modifier input, never as an absolute gate.
- `pandas.Series.ewm` MUST be default smoothing implementation for eligible series.
- `statsmodels.tsa.seasonal.STL` MUST be used for monthly/weekly eligible seasonal adjustment.
- `statsmodels.tsa.seasonal.MSTL` MUST be used for regular sub-daily eligible seasonal adjustment.
- `ruptures` MUST be used only for additive change-point metadata and limited tie-break/context behavior.
- `statsmodels` OLS diagnostics MUST be computed and exposed as supplementary evidence fields (detail/as-of only).
- Outdated tools (`pymannkendall`, `mannkendall`, `kats`) MUST NOT be introduced in this feature.

## Execution Guidance (Mandatory)

- Implement with red/green TDD by workstream.
- Keep canonical contract changes and cross-layer propagation in same release unit.
- Preserve single outward canonical descriptor semantics across all endpoints and UI consumers.
- Validate with local runtime restart discipline before stop gates:
  - `docker compose down`
  - `docker compose up -d`
- Before commit or handoff, run:
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
