# Implementation Plan: Gap-Tolerant Cadence Inference

**Branch**: `047-handle-cadence-gaps` | **Date**: 2026-04-05 | **Spec**: `/root/snap/longtail-experiment/specs/047-handle-cadence-gaps/spec.md`
**Input**: Feature specification from `/specs/047-handle-cadence-gaps/spec.md`

## Summary

Update cadence inference used by trend processing so isolated historical gaps are treated as tolerable gaps rather than automatic irregular-spacing failures, while preserving strict rejection for truly mixed cadence histories. The plan introduces a ratio-based irregular-gap threshold with deterministic dominant-cadence validation, applies the same policy in backfill and incremental runtime paths, and surfaces explicit cadence decision metadata in run outcomes for operator transparency.

Threshold selected for this plan: `0.20%` maximum irregular-gap ratio (`MAX_IRREGULAR_GAP_RATIO = 0.002`).

## Technical Context

**Language/Version**: Python 3.12 (library + pipeline runtime)  
**Primary Dependencies**: `libs/trend_analysis` cadence/classifier logic, Dagster ingest orchestration, pipeline trend runtime processor, pytest, Ruff, Ty  
**Storage**: PostgreSQL 16 runtime/trend persistence and run outcome tables (`ingestion_runs`, `source_run_outcomes`, trend tables)  
**Testing**: `pytest` for `libs/trend_analysis` and `apps/pipeline`, local compose ingest verification, `pre-commit run --all-files`, Nx full-suite and coverage gates  
**Target Platform**: Linux local development via unified Docker Compose stack
**Project Type**: Nx monorepo backend/pipeline vertical slice (no frontend scope)  
**Performance Goals**: Eliminate false cadence-irregular failures for isolated-gap regular series while keeping deterministic trend processing outcomes and no material runtime regressions  
**Constraints**: Preserve existing hard-failure behavior for non-increasing periods and insufficient observations; preserve true-irregular rejection; maintain >=90% coverage and mandatory monorepo stop gates  
**Scale/Scope**: Cadence policy in shared trend-analysis library and pipeline runtime integration across grouped sources (including EIA/FRED reference sources)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Changes stay within existing `libs/trend_analysis` and `apps/pipeline` boundaries, with coordinated runtime and test updates.
- Quality gate enforcement: PASS. Plan requires standard lint/format/typecheck/test flows with no suppressions or bypasses.
- Full-suite stop rule: PASS. Plan requires `pnpm exec nx run-many -t test --all` before commit and before agent handoff/end.
- Coverage stop rule: PASS. Plan requires `pnpm exec nx run-many -t coverage --all` before commit with >=90% per-project thresholds.
- Test and coverage discipline: PASS. Plan includes library and runtime automated tests for tolerated-gap acceptance, true-irregular rejection, and deterministic rerun behavior.
- Local-first parity: PASS. End-to-end behavior is validated through the existing Docker Compose stack and real ingest execution.
- Data integrity and reliability: PASS. Cadence decision logic remains deterministic, explicit, and auditable, with no silent relaxations.
- Configuration integrity: PASS. No new secret-bearing services or env vars are introduced; existing fail-fast credential policy remains unchanged.
- Frontend UI consistency: PASS (N/A). No frontend changes are in scope.
- Documentation fidelity: PASS. Plan includes research, data model, contract, quickstart, and agent context refresh.

## Project Structure

### Documentation (this feature)

```text
specs/047-handle-cadence-gaps/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cadence-gap-tolerance.contract.yaml
└── tasks.md
```

### Source Code (repository root)

```text
libs/trend_analysis/
├── src/trend_analysis/
│   ├── cadence.py
│   └── classifier.py
└── tests/
    ├── test_cadence_and_failures.py
    └── test_multi_lookback_classifier.py

apps/pipeline/
├── src/orchestration/jobs/
│   ├── trend_runtime_processor.py
│   ├── source_ingest_runner.py
│   └── parallel_source_executor.py
└── tests/orchestration/
    ├── test_trend_runtime_processor.py
    └── test_trend_asset_failure_scope.py
```

**Structure Decision**: Deliver as a pipeline/library reliability refinement. Cadence-policy behavior is centralized in the shared trend-analysis library, then exercised via existing runtime orchestration paths and run-outcome reporting.

## Phase Plan

### Phase 0: Research and Decision Locking

- Lock cadence decision policy for isolated-gap treatment versus true irregular rejection.
- Measure reference EIA irregular-gap ratio and use it to select a bounded tolerance threshold.
- Confirm policy determinism requirements and metadata expectations.
- Output: `specs/047-handle-cadence-gaps/research.md`.

### Phase 1: Design and Contracts

- Define cadence decision and policy entities in `data-model.md`.
- Define cadence decision contract and fixed policy constants in `contracts/cadence-gap-tolerance.contract.yaml`.
- Define runtime verification steps in `quickstart.md`.
- Refresh agent context with `.specify/scripts/bash/update-agent-context.sh codex`.

### Phase 2: Implementation Planning

#### Workstream A: Cadence policy update in shared trend library

1. Add gap-tolerant cadence decision logic to cadence inference, including:
   - dominant cadence-family requirement
   - irregular-gap ratio computation
   - threshold comparison against `0.20%`
2. Preserve existing failures for:
   - insufficient observations
   - non-increasing periods
   - mixed cadence families that are not isolated-gap candidates
3. Add deterministic reason coding for cadence outcomes (`regular`, `gap_tolerant`, `irregular_rejected`).

#### Workstream B: Runtime propagation and source outcome alignment

1. Ensure runtime trend processing uses the updated cadence policy in both backfill and incremental evaluations.
2. Propagate cadence-decision metadata into series/source outcome context so operators can see why a series passed or failed.
3. Preserve source-level failure behavior for truly irregular cadence.
4. Ensure isolated-gap accepted series do not emit `trend_processing_failed` for irregular spacing.

#### Workstream C: Test and validation hardening

1. Library tests:
   - isolated-gap acceptance under threshold
   - true-irregular rejection over threshold
   - dominant-cadence enforcement
2. Pipeline tests:
   - runtime continuation for gap-tolerant series
   - branch-scoped failure for truly irregular series
3. Local runtime verification:
   - rerun ingest and validate EIA/FRED outcomes for reference series
   - verify cadence decision metadata in run outcomes

## Threshold Justification

- Reference series: `ENERGY.US.RETAIL_GASOLINE.NUS`.
- Measured intervals: `1852`.
- Measured irregular intervals: `1`.
- Measured irregular ratio: `0.0540%`.
- Planned threshold: `0.20%`.
- Relationship to reference: threshold is about `3.7x` the observed ratio, allowing a little more room for slightly gappier but still practically regular data while keeping tolerance very strict (>99.8% intervals must still align to cadence rules).

## Future Data Risk Note

- This plan intentionally calibrates tolerance using current known dataset behavior (including the EIA reference gap profile).
- If incoming providers or historical backfills introduce substantially more irregular or differently shaped gaps, the current ratio-based policy may underfit or overfit real cadence quality.
- The implementation should therefore be treated as an initial policy baseline, with explicit expectation of a future policy revision if the observed data distribution shifts.

## Execution Guidance (Mandatory)

- Use red/green TDD for cadence library and runtime integration slices.
- Keep policy constants centralized so backfill/incremental paths cannot drift.
- Validate with real ingest execution before final quality gates.
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
- Frontend UI consistency: PASS (N/A)
- Documentation fidelity: PASS

## Complexity Tracking

No constitution violations requiring justification.
