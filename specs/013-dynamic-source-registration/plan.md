# Implementation Plan: Dynamic Source Workflow Registration

**Branch**: `013-dynamic-source-registration` | **Date**: 2026-03-22 | **Spec**: `specs/013-dynamic-source-registration/spec.md`
**Input**: Feature specification from `/specs/013-dynamic-source-registration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace hard-coded source workflow bootstrap wiring with deterministic discovery-based registration so compliant source adapters can be onboarded without runtime bootstrap edits. The implementation centers on a single discovery/registration entrypoint, strict contract validation with actionable failures, duplicate source-key guardrails, and documentation/test updates that preserve existing source behavior.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 (pipeline/backend), TypeScript 5.x unchanged  
**Primary Dependencies**: Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, psycopg 3.x, structlog, OpenTelemetry API/SDK, uv, pytest, Nx tooling  
**Storage**: PostgreSQL 16 runtime store plus canonical observation store (`source_profiles`, `data_series`, `observations`)  
**Testing**: pytest + pytest-cov in pipeline/backend, orchestration smoke tests, Nx affected quality targets, local-stack scripts  
**Target Platform**: Local-first macOS/Linux developer environments and CI runners
**Project Type**: Nx monorepo data-platform orchestration/runtime feature  
**Performance Goals**: deterministic registration order in 100% of repeated startup runs; malformed/duplicate adapter failures in 100% of negative tests with actionable diagnostics  
**Constraints**: preserve existing source execution/scheduling semantics; no quality-gate bypasses; maintain >=90% coverage on affected projects; no regression in local Dagit workspace load  
**Scale/Scope**: initial scope covers existing active adapters (`dummy_source`, `example_source`, `fred_fedfunds`) plus forward onboarding pattern for additional modules under `apps/pipeline/src/orchestration/jobs/sources/`

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

- Monorepo cohesion: PASS. Work stays within existing pipeline and docs boundaries and preserves current Nx project layout.
- Quality gate enforcement: PASS. Plan relies on existing lint/format/typecheck/test gates with no suppressions.
- Test and coverage discipline: PASS. Plan adds/updates orchestration tests for discovery, contract validation, deterministic ordering, and smoke assertions.
- Local-first parity: PASS. Plan includes local Dagit verification and compose-stack checks.
- Data integrity and reliability: PASS. Registration composition changes are isolated from ingest/persistence semantics; duplicate guardrails remain enforced.
- Documentation fidelity: PASS. Plan includes runbook onboarding updates and any required AGENTS updates if workflow commands change.

## Project Structure

### Documentation (this feature)

```text
specs/013-dynamic-source-registration/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── source-registration-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
apps/
└── pipeline/
  ├── src/
  │   └── orchestration/
  │       ├── runtime.py
  │       └── jobs/
  │           └── source_assets/
  │               ├── discovery.py
  │               └── contracts.py
  └── tests/
    └── orchestration/
      ├── test_source_asset_discovery.py
      ├── test_source_asset_contract_validation.py
      └── test_definitions_smoke.py

docs/
├── runbooks/
│   └── local-stack-baseline.md
└── runbooks/
  └── provider-onboarding.md
```

**Structure Decision**: Extend current orchestration runtime composition in place by centralizing discovery/contract registration paths in existing `source_assets` modules and validating through orchestration tests. No new app/library boundaries are introduced.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Resolve registration composition decisions before implementation:

- Discovery model selection and deterministic ordering rule.
- Adapter contract validation scope and actionable failure structure.
- Non-adapter file handling policy.
- Smoke-test assertion strategy that avoids hard-coding runtime imports while preserving expected source visibility.

Output captured in `research.md`.

## Phase 1: Design & Contracts

### Data Model

Define discovery and registration entities (adapter candidate, contract validation result, registration catalog snapshot, startup failure record) and their invariants in `data-model.md`.

### Interface Contracts

Define the source registration contract and failure semantics in `contracts/source-registration-contract.md`.

### Quickstart

Define local validation flow for dynamic registration behavior, malformed adapter fail-fast checks, duplicate-key rejection, and Dagit visibility checks in `quickstart.md`.

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

1. Runtime composition cleanup to use single discovery/registration entrypoint.
2. Adapter discovery behavior for valid/invalid/non-adapter modules with deterministic ordering.
3. Contract failure diagnostics and duplicate identity rejection checks.
4. Smoke and orchestration tests updated for dynamic registration expectations.
5. Onboarding/runbook documentation updates for the new provider onboarding flow.

## Implementation Finalization Notes

- This feature changes registration composition ergonomics only; source execution semantics and persistence behavior remain unchanged.
- Existing adapters must continue to register and execute successfully under the new discovery flow.
