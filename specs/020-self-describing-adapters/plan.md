# Implementation Plan: Self-Describing Source Adapters

**Branch**: `020-self-describing-adapters` | **Date**: 2026-03-23 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/020-self-describing-adapters/spec.md`

## Summary

Eliminate all five manually-edited bootstrap surfaces from the Dagster ingestion pipeline
so that onboarding a new data source requires creating exactly one file: an adapter
module. The adapter exports a `SOURCE_SPEC: SourceBuilderSpec` that the runtime
discovers, validates, and wires automatically. Two new fields (`cron_schedule`,
`cadence_label`) are added to the `SourceBuilderSpec` dataclass; a dynamic filesystem
scan replaces `_build_default_specs()`; and schedules, Dagit assets, the workspace
catalog, and the runtime wiring verification are all derived from discovered adapter
manifests. The FRED adapter is migrated to the new self-describing format as the
reference implementation, removing all hardcoded FRED-specific entries from every
non-adapter file.

## Technical Context

**Language/Version**: Python 3.12 (`apps/pipeline`)  
**Primary Dependencies**: Dagster 1.x, dataclasses (stdlib), importlib (stdlib), pathlib (stdlib)  
**Storage**: No schema changes. PostgreSQL 16 canonical tables unchanged.  
**Testing**: pytest + pytest-cov; all pipeline tests in `apps/pipeline/tests/orchestration/`  
**Target Platform**: Linux (Docker Compose local stack), Dagit operator UI  
**Project Type**: Dagster orchestration pipeline (monorepo app)  
**Performance Goals**: Discovery scan completes in < 100ms; cached after first call  
**Constraints**: Zero DB migrations. No new Compose services. All changes within `apps/pipeline/` and docs/skills.  
**Scale/Scope**: Currently 1 adapter (FRED). Design must support N adapters generically.

## Constitution Check

_GATE: All checks pass. Ready for Phase 0 research and Phase 1 design._

| Check                                                                                                                  | Status  | Notes                                                                                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Monorepo cohesion (Nx boundaries, vertical-slice contracts)                                                            | ✅ PASS | All changes within `apps/pipeline/`. No cross-project contract changes. `libs/db` and `apps/backend` unaffected.                                                                  |
| Quality gate enforcement (lint, format, typecheck, test — no suppressions)                                             | ✅ PASS | No new lint suppressions required. Moving `ObservationCheckpointRepository` resolves the existing cross-layer import. ruff and ty will be satisfied by proper Protocol placement. |
| Full-suite stop rule (`pnpm exec nx run-many -t test --all`)                                                           | ✅ PASS | Plan requires full-suite gate before every commit and before agent handoff.                                                                                                       |
| Coverage stop rule (`pnpm exec nx run-many -t coverage --all` ≥ 90%)                                                   | ✅ PASS | Negative-path tests for startup validation (missing fields, duplicate keys, malformed cron) cover the new `scan_adapter_modules` and `_validate_adapter_specs` code paths.        |
| Test and coverage discipline (≥ 90% per project)                                                                       | ✅ PASS | New functions in `discovery.py` covered by new unit tests. Dynamic schedule/asset factory functions covered by smoke tests.                                                       |
| Local-first parity (runnable via Docker Compose)                                                                       | ✅ PASS | No new compose services required. FRED ingest continues to work in local stack post-migration.                                                                                    |
| Data integrity and reliability (schema/contract versioning)                                                            | ✅ PASS | Zero schema changes. Observation persistence, series catalog, and provenance tracking unaffected.                                                                                 |
| Documentation fidelity (`provider-onboarding.md`, `local-stack-baseline.md`, `AGENTS.md`, `onboard-provider/SKILL.md`) | ✅ PASS | All four explicitly included in Phase 8 of implementation plan. FR-012 mandates this.                                                                                             |

_Post-design re-check_: No constitution violations introduced by the Phase 1 design.
`ObservationCheckpointRepository` correctly moved to the infrastructure layer. No new
external dependencies; no circular imports in test-verified import chain.

## Project Structure

### Documentation (this feature)

```text
specs/020-self-describing-adapters/
├── plan.md                               # This file
├── research.md                           # Phase 0 — all decisions resolved
├── data-model.md                         # Phase 1 — changed/new types
├── quickstart.md                         # Phase 1 — single-step onboarding guide
├── contracts/
│   └── adapter-manifest-contract.md      # Phase 1 — SOURCE_SPEC contract spec
├── checklists/
│   └── requirements.md                   # Quality checklist (all items passing)
└── tasks.md                              # Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Source Code (apps/pipeline — all changes confined here)

```text
apps/pipeline/src/orchestration/
├── jobs/
│   ├── source_assets/
│   │   ├── discovery.py          # MODIFIED: +scan_adapter_modules, +SourceAdapterManifestError,
│   │   │                         #           +ObservationCheckpointRepository (moved from FRED),
│   │   │                         #           +cron_schedule/cadence_label fields on SourceBuilderSpec,
│   │   │                         #           -_build_default_specs (replaced by scan)
│   │   └── contracts.py          # UNCHANGED (register_source_assets, SourceAssetContractError)
│   └── sources/
│       └── fred_fedfunds_source.py  # MODIFIED: +SOURCE_SPEC, ObservationCheckpointRepository
│                                    #            imported from discovery.py (not defined here)
├── schedules/
│   └── source_asset_schedules.py   # MODIFIED: remove hardcoded dicts + variable;
│                                   #            SOURCE_ASSET_SCHEDULES derived from scan
├── source_asset_definitions.py     # MODIFIED: remove @asset functions; SOURCE_DAGIT_ASSETS
│                                   #            derived from scan via factory
├── definitions.py                  # MODIFIED: WORKSPACE_DEFINITION_CATALOG derived from scan
└── runtime.py                      # MODIFIED: EXPECTED_RUNTIME_SOURCE_KEYS derived from scan;
                                    #            remove FRED_FEDFUNDS_SOURCE_KEY import

apps/pipeline/tests/orchestration/
├── test_source_asset_discovery.py        # MODIFIED: update assertions for scan-based model
├── test_definitions_smoke.py             # MODIFIED: update catalog/key assertions for scan-based model
├── test_execution_primitives.py          # MODIFIED: update schedule/asset helper tests for manifest-driven APIs
├── test_source_cadence_selection.py      # MODIFIED: remove static cadence dict assertions; derive cadence from manifests
├── test_source_asset_contract_validation.py  # UNCHANGED
├── test_adapter_manifest_validation.py   # NEW: startup validation positive and negative paths
└── test_single_file_onboarding_guard.py  # NEW: anti-hardcoding guard + one-file onboarding acceptance harness

docs/runbooks/
├── provider-onboarding.md               # MODIFIED: collapse 8 steps → 1 step
└── local-stack-baseline.md              # MODIFIED: remove outdated multi-file onboarding steps

.agents/skills/onboard-provider/
└── SKILL.md                             # MODIFIED: reflect single-file model

AGENTS.md                                # MODIFIED: update Recent Changes section
```

**Structure Decision**: Single Nx project (`pipeline`). All changes within
`apps/pipeline/`. No new modules, directories, or compose services.

## Complexity Tracking

No constitution violations. No complexity exceptions required.

---

## Implementation Phases

### Phase 1 — Manifest Contract: Extend `SourceBuilderSpec` and Move Protocol

**Goal**: Establish the data type and Protocol that all subsequent phases depend on.
No behavioral changes yet.

**Files changed**:

#### `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`

1. Add `SourceAdapterManifestError(Exception)` class.
2. Move `ObservationCheckpointRepository` Protocol into this file (currently defined in
   `fred_fedfunds_source.py`). Remove the duplicate from the FRED adapter in Phase 3.
3. Add two fields to `SourceBuilderSpec`:
   - `cron_schedule: str = ""`
   - `cadence_label: str = ""`

**Tests**: No new tests needed in this phase — the type changes are backward-compatible
(new fields have defaults). Existing tests still pass unmodified.

**Acceptance**: `ty check apps/pipeline` passes with new fields and Protocol in place.

---

### Phase 2 — Dynamic Discovery Engine

**Goal**: Replace `_build_default_specs()` with `scan_adapter_modules()` that scans the
filesystem, imports each `*_source.py` module, reads its `SOURCE_SPEC`, validates it,
and returns a cached sorted tuple.

**Files changed**:

#### `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`

1. Add module-level sentinel: `_CACHED_ADAPTER_SPECS: tuple[SourceBuilderSpec, ...] | None = None`
2. Implement `_get_sources_directory() -> Path` — returns the `jobs/sources/` path.
   Isolated for testability (can be monkey-patched).
3. Implement `_do_scan() -> tuple[SourceBuilderSpec, ...]`:
   - `glob("*_source.py")` in sources directory
   - For each file, compute module path: `src.orchestration.jobs.sources.{stem}`
   - `importlib.import_module(module_path)`
   - Read `SOURCE_SPEC` attribute; if missing, record validation error
   - Collect `(module_path, spec)` pairs
   - Call `_validate_adapter_specs(pairs)` — raise if violations
   - Return sorted by `spec.source_key`
4. Implement `_validate_adapter_specs(pairs: list[tuple[str, SourceBuilderSpec]]) -> None`:
   - Collect all violations across all adapters before raising
   - Checks: non-empty `source_key`, non-empty `provider_group_key`, len(series) >= 1,
     series length parity, non-empty `cron_schedule`, non-empty `cadence_label`, unique
     `source_key` across all adapters
   - Raise `SourceAdapterManifestError` with all messages joined
5. Implement `scan_adapter_modules() -> tuple[SourceBuilderSpec, ...]`:
   - Check `_CACHED_ADAPTER_SPECS`; call `_do_scan()` on first invocation; cache and return
6. Implement `_clear_scan_cache() -> None` — test-only cache reset
7. Replace `_build_default_specs()` body with `return scan_adapter_modules()` (or inline
   `specs or scan_adapter_modules()` in the callers) — preserve the `specs` override
   path in `discover_source_registrations` and `discover_series_catalog_entries` for
   test inject ability.

**New test file**: `apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py`

Tests to write:

- `test_scan_finds_fred_adapter_by_default` — default scan returns `fred_fedfunds`
- `test_scan_result_is_cached` — two calls return same object identity
- `test_clear_cache_allows_rescan` — `_clear_scan_cache()` → second scan re-runs
- `test_validation_rejects_missing_source_key` — inject spec with empty `source_key`
- `test_validation_rejects_empty_series` — inject spec with `series_item_keys=()`
- `test_validation_rejects_series_length_mismatch` — 2 item keys, 1 canonical key
- `test_validation_rejects_empty_cron_schedule` — empty `cron_schedule`
- `test_validation_rejects_invalid_cron_syntax` — malformed cron string includes module + value in error
- `test_validation_rejects_empty_cadence_label` — empty `cadence_label`
- `test_validation_rejects_duplicate_source_key` — two specs same `source_key`
- `test_validation_collects_all_errors` — two broken specs → both errors in message
- `test_validation_rejects_missing_SOURCE_SPEC_attribute` — module without `SOURCE_SPEC`
- `test_scan_ignores_non_source_modules` — helper file not ending in `_source.py`
- `test_scan_order_is_deterministic_alphabetical` — inject two specs; verify sort order

**Acceptance**: All new tests pass. `test_source_asset_discovery.py` still passes
(existing `specs=` override tests unaffected). `scan_adapter_modules()` exported.

---

### Phase 3 — Migrate FRED Adapter to Self-Describing Format

**Goal**: Add `SOURCE_SPEC` to `fred_fedfunds_source.py` and update its imports.
After this phase, `discovery.py` has zero static imports from adapter modules.

**Files changed**:

#### `apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py`

1. Remove the `ObservationCheckpointRepository` Protocol definition (now in `discovery.py`).
2. Add import: `from ..source_assets.discovery import ObservationCheckpointRepository, SourceBuilderSpec`
3. Add module-level `SOURCE_SPEC: SourceBuilderSpec = SourceBuilderSpec(...)` with all
   fields populated from existing constants (`FRED_FEDFUNDS_SOURCE_KEY`, `FRED_SERIES_CONFIGS`):

   ```python
   SOURCE_SPEC = SourceBuilderSpec(
       source_key=FRED_FEDFUNDS_SOURCE_KEY,
       module_name="src.orchestration.jobs.sources.fred_fedfunds_source",
       builder=lambda runner, obs_repo: build_fred_fedfunds_source_workflow(
           runner,
           observation_repository=obs_repo,
           schedule_policy=SourceSchedulePolicy(
               source_key=FRED_FEDFUNDS_SOURCE_KEY,
               cadence_type="daily",
           ),
       ),
       provider_group_key="fred",
       series_item_keys=tuple(cfg["series_item_key"] for cfg in FRED_SERIES_CONFIGS),
       canonical_series_keys=tuple(cfg["canonical_series_key"] for cfg in FRED_SERIES_CONFIGS),
       ownership_mode="grouped",
       cron_schedule="0 0 * * *",
       cadence_label="daily",
   )
   ```

#### `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`

1. Remove: `from ..sources.fred_fedfunds_source import (FRED_FEDFUNDS_SOURCE_KEY, ObservationCheckpointRepository, build_fred_fedfunds_source_workflow)`
   (These were used only by `_build_default_specs()` which is now replaced by `scan_adapter_modules()`.)
2. Keep `ObservationCheckpointRepository` defined here (moved in Phase 1).

#### `apps/pipeline/src/orchestration/runtime.py`

1. Remove: `from .jobs.sources.fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY`
   (Used only by `EXPECTED_RUNTIME_SOURCE_KEYS` which is updated in Phase 6.)

**Tests**: No new tests needed. `test_adapter_manifest_validation.py::test_scan_finds_fred_adapter_by_default`
verifies the FRED `SOURCE_SPEC` is correctly read. Existing FRED ingest tests continue to
pass because the builder function is unchanged.

**Acceptance**: `discovery.py` has no static imports from any adapter module. `ty check` passes.

---

### Phase 4 — Dynamic Schedule Generation

**Goal**: Remove hardcoded schedule entries from `source_asset_schedules.py`. Build
`SOURCE_ASSET_SCHEDULES` dynamically from adapter manifests.

**Files changed**:

#### `apps/pipeline/src/orchestration/schedules/source_asset_schedules.py`

Complete replacement. Remove:

- `SOURCE_CADENCE_DEFINITIONS` dict
- `SOURCE_SERIES_ITEM_DEFINITIONS` dict
- `SOURCE_PROVIDER_GROUP_DEFINITIONS` dict
- `fred_fedfunds_schedule` variable

Replace with:

```python
from __future__ import annotations
from dagster import RunRequest, schedule
from ..jobs.source_assets.discovery import SourceBuilderSpec, scan_adapter_modules


def _make_source_schedule(spec: SourceBuilderSpec):
    @schedule(
        cron_schedule=spec.cron_schedule,
        job_name="ingest_job",
        name=f"{spec.source_key}_schedule",
    )
    def source_schedule(_context) -> RunRequest:
        return RunRequest(
            run_key=None,
            tags={
                "trigger_type": "scheduled",
                "source_selection_mode": "source_owned",
                "requested_by": f"{spec.source_key}_schedule",
                "source_keys": spec.source_key,
                "cadence_label": spec.cadence_label,
                "provider_group_key": spec.provider_group_key,
                "series_item_keys": ",".join(spec.series_item_keys),
            },
        )
    source_schedule.__doc__ = (
        f"Emit scheduled run requests for {spec.source_key} ({spec.cadence_label})."
    )
    return source_schedule


SOURCE_ASSET_SCHEDULES = [
    _make_source_schedule(spec) for spec in scan_adapter_modules()
]
```

**Test updates**: `test_definitions_smoke.py` imports `SOURCE_CADENCE_DEFINITIONS` and
`SOURCE_SERIES_ITEM_DEFINITIONS`. Update to get cadence/series from `scan_adapter_modules()`
or the Definitions object directly.

**Acceptance**: `defs` (Dagster `Definitions`) contains schedule names that match
`{source_key}_schedule` for each discovered adapter. Smoke tests pass.

---

### Phase 5 — Dynamic Dagit Asset Generation

**Goal**: Remove hand-written `@asset` functions from `source_asset_definitions.py`.
Build `SOURCE_DAGIT_ASSETS` dynamically from adapter manifests.

**Files changed**:

#### `apps/pipeline/src/orchestration/source_asset_definitions.py`

Remove:

- `from .schedules.source_asset_schedules import SOURCE_CADENCE_DEFINITIONS`
- `fred_fedfunds_source_asset` function
- `fred_gasregw_source_asset` function

Replace with factory and dynamic list:

```python
from __future__ import annotations
from typing import Any
from dagster import asset
from .jobs.source_assets.discovery import SourceBuilderSpec, scan_adapter_modules


def _asset_name_from_series_item_key(
    series_item_key: str,
    provider_group_key: str,
) -> str:
    prefix = f"{provider_group_key}_"
    return series_item_key.removeprefix(prefix) if series_item_key.startswith(prefix) else series_item_key


def _make_asset_for_series_item(spec: SourceBuilderSpec, series_item_key: str):
    name = _asset_name_from_series_item_key(series_item_key, spec.provider_group_key)

    @asset(name=name, key_prefix=spec.provider_group_key, required_resource_keys={"run_coordinator"})
    def _series_asset(context) -> dict[str, Any]:
        summary = context.resources.run_coordinator.run(
            trigger_type="on_demand",
            requested_by="dagit_series_materialization",
            source_keys=[spec.source_key],
            series_item_keys=[series_item_key],
        )
        return {
            "run_id": summary["run_id"],
            "source_key": spec.source_key,
            "series_item_key": series_item_key,
            "outcome_state": summary["outcome_state"],
            "executed_source_count": summary["executed_source_count"],
            "failed_source_count": summary["failed_source_count"],
            "schedule_cadence": spec.cadence_label,
            "schedule_owner": f"{spec.source_key}_schedule",
        }

    _series_asset.__name__ = f"{spec.source_key}_{series_item_key}_asset"
    _series_asset.__doc__ = f"Materialize source visibility entry for {series_item_key}."
    return _series_asset


SOURCE_DAGIT_ASSETS = [
    _make_asset_for_series_item(spec, series_item_key)
    for spec in scan_adapter_modules()
    for series_item_key in spec.series_item_keys
]
```

**Test updates**: Smoke test assertions on `fred/fedfunds` and `fred/gasregw` asset keys
continue to hold (key derivation logic produces the same result).

**Acceptance**: `defs.resolve_all_asset_keys()` includes `fred/fedfunds` and `fred/gasregw`.
Smoke test assertions pass.

---

### Phase 6 — Eliminate Catalog and Wiring Hardcoding

**Goal**: Remove the last two hardcoded bootstrap artifacts (`WORKSPACE_DEFINITION_CATALOG`
and `EXPECTED_RUNTIME_SOURCE_KEYS`).

**Files changed**:

#### `apps/pipeline/src/orchestration/definitions.py`

Replace hardcoded `WORKSPACE_DEFINITION_CATALOG` with derived version:

```python
from .jobs.source_assets.discovery import scan_adapter_modules

def _derive_asset_keys(specs) -> tuple[str, ...]:
    keys = []
    for spec in specs:
        prefix = spec.provider_group_key
        for sik in spec.series_item_keys:
            name = sik.removeprefix(f"{prefix}_") if sik.startswith(f"{prefix}_") else sik
            keys.append(f"{prefix}/{name}")
    return tuple(sorted(keys))

_specs = scan_adapter_modules()
WORKSPACE_DEFINITION_CATALOG: dict[str, tuple[str, ...]] = {
    "jobs": ("ingest_job",),
    "assets": _derive_asset_keys(_specs),
    "schedules": tuple(f"{spec.source_key}_schedule" for spec in _specs),
    "sensors": ("ondemand_sensor",),
}
```

#### `apps/pipeline/src/orchestration/runtime.py`

Remove `from .jobs.sources.fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY` (done in Phase 3).

Replace `EXPECTED_RUNTIME_SOURCE_KEYS`:

```python
from .jobs.source_assets.discovery import scan_adapter_modules
EXPECTED_RUNTIME_SOURCE_KEYS = tuple(spec.source_key for spec in scan_adapter_modules())
```

**Test updates**:

- `test_definitions_smoke.py`: Update `test_runtime_builder_registers_expected_sources`
  to derive expected keys from `scan_adapter_modules()` rather than importing
  `FRED_FEDFUNDS_SOURCE_KEY`.
- Any test asserting on `WORKSPACE_DEFINITION_CATALOG` content updates to derive from scan.

**Acceptance**: All five previously-hardcoded files compile and pass `ty check` with zero
FRED-specific string literals remaining. `grep -r "fred_fedfunds" apps/pipeline/src/orchestration/definitions.py`
returns nothing.

---

### Phase 7 — Test Suite Finalization and Coverage

**Goal**: Ensure the complete test suite passes at 90%+. No test suppression or bypass.

**Test file updates summary**:

| File                                   | Changes                                                                                                                                                            |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `test_source_asset_discovery.py`       | Update `test_discovery_returns_deterministic_source_order` to derive expected source keys from `scan_adapter_modules()` instead of hardcoding `["fred_fedfunds"]`. |
| `test_definitions_smoke.py`            | Remove `SOURCE_CADENCE_DEFINITIONS` / `SOURCE_SERIES_ITEM_DEFINITIONS` imports; derive schedule/asset expectations from scan.                                      |
| `test_execution_primitives.py`         | Replace static `_make_source_schedule("fred_fedfunds", ...)` and direct `fred_*_source_asset` assumptions with manifest-driven helper assertions.                  |
| `test_source_cadence_selection.py`     | Remove `SOURCE_CADENCE_DEFINITIONS` imports and assert cadence ownership using discovered adapter manifest metadata.                                               |
| `test_adapter_manifest_validation.py`  | New. All 13 negative/positive path tests from Phase 2.                                                                                                             |
| `test_single_file_onboarding_guard.py` | New. Enforce zero source-specific hardcoding in the five bootstrap files and verify one-file onboarding acceptance path.                                           |

**Coverage check**:

```bash
pnpm exec nx run-many -t coverage --all
```

`apps/pipeline` must remain ≥ 90%.

---

### Phase 8 — Documentation and Skill Updates

**Goal**: Update all human-facing documentation to reflect the single-file onboarding
model. This phase is deliverable in the same commit as the code changes.

#### `docs/runbooks/provider-onboarding.md`

- Remove Steps 2–8 (all bootstrap edits: discovery.py, schedules, asset definitions,
  definitions.py, runtime.py, smoke test updates, Dagit start)
- Replace with the single-step model from `specs/020-self-describing-adapters/quickstart.md`
- Add troubleshooting table
- Update "Files NOT to Edit" section

#### `docs/runbooks/local-stack-baseline.md`

- Remove onboarding instructions that require discovery/schedules/asset/catalog edits
- Replace with reference to single-file adapter workflow and verification commands
- Ensure source onboarding section matches `provider-onboarding.md` exactly

#### `AGENTS.md`

- Update `## Recent Changes` to document feature 020
- Update any mentions of multi-file onboarding steps in the active technologies blurb

#### `.agents/skills/onboard-provider/SKILL.md`

- Remove all bootstrap steps (Steps 2–8) from Phase 2 or the integration phase
- Replace with: "Create adapter module with SOURCE_SPEC" as the sole action
- Update Phase 3 standalone validation to reference `scan_adapter_modules()` smoke check
- Preserve feasibility assessment, dimensionality guidance, and Phase 1 profile table

---

## Risk Register

| Risk                                                                               | Likelihood | Mitigation                                                                                                                                                  |
| ---------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Circular import at import time                                                     | Low        | Verified: `ObservationCheckpointRepository` moved to `discovery.py`; FRED imports from `discovery.py`; `discovery.py` does not statically import from FRED. |
| Scan cache creates test isolation issues                                           | Medium     | `_clear_scan_cache()` test helper provided. Test that patches sources dir must call it in teardown.                                                         |
| Dynamic `@asset` names differ from hand-written ones                               | Low        | Name derivation logic (`removeprefix`) produces identical names to hand-written functions. Covered by smoke test.                                           |
| `WORKSPACE_DEFINITION_CATALOG` keys are computed in wrong order                    | Low        | `_derive_asset_keys` sorts before returning; `test_definitions_smoke.py` verifies set membership not order.                                                 |
| pytest isolation: `scan_adapter_modules()` returns stale cached state across tests | Medium     | Tests that inject custom specs via the `specs=` override parameter are unaffected. Only tests exercising the real filesystem scan need cache management.    |

---

## Commit Strategy

All eight implementation phases are deliverable in a single commit on
`020-self-describing-adapters`. The commit MUST satisfy:

1. `pnpm exec nx run-many -t test --all` — full suite passes
2. `pnpm exec nx run-many -t coverage --all` — `apps/pipeline` ≥ 90%
3. `uv run --project apps/pipeline ruff check apps/pipeline` — zero violations
4. `uv run --project apps/pipeline ruff format --check apps/pipeline` — clean
5. `uv run --project apps/pipeline ty check apps/pipeline` — zero type errors

No partial commits that leave any bootstrap surface in an inconsistent state are allowed.
