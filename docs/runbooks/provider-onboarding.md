# Provider Onboarding Runbook

This guide covers the end-to-end process for adding a new ingestion provider (or new series under an existing provider) to the Dagster orchestration runtime.

## What Is and Isn't Automated

**Automatically handled by dynamic registration** (no bootstrap edits required):

- Runtime workflow registration — discovery scans `jobs/sources/*_source.py` modules and loads each module `SOURCE_SPEC`.
- Schedule derivation — `SOURCE_CADENCE_DEFINITIONS`, provider-group tags, and `SOURCE_ASSET_SCHEDULES` are built from discovered specs.
- Dagit asset derivation — `SOURCE_DAGIT_ASSETS` are generated from `SOURCE_SPEC.series_item_keys`.
- Workspace catalog derivation — `WORKSPACE_DEFINITION_CATALOG` derives assets/schedules from generated definitions.
- Duplicate source-key detection — the contract guard will fail fast at startup if `source_key` collides.
- Deterministic registration ordering — discovery sorts by `source_key`; startup order is stable.

> **Naming constraint**: The source module filename **must end in `_source.py`** (e.g. `acme_cpi_source.py`). The `is_adapter_spec()` filter in `discovery.py` enforces this to avoid accidentally including helper or utility modules in adapter discovery.

**Still requires explicit code additions** for each new provider:

| Surface                       | File                                                                | Required                 |
| ----------------------------- | ------------------------------------------------------------------- | ------------------------ |
| Source adapter implementation | `apps/pipeline/src/orchestration/jobs/sources/<provider>_source.py` | Always                   |
| DB model + Alembic migration  | `libs/db/src/db/models/`, `libs/db/alembic/versions/`               | Only when schema changes |

## Data Model Terms

Use these keys consistently throughout all files:

| Term                   | Meaning                                                                 | Example             |
| ---------------------- | ----------------------------------------------------------------------- | ------------------- |
| `source_key`           | Workflow registration and schedule identity                             | `fred_fedfunds`     |
| `provider_group_key`   | Grouping key for related series sharing a provider                      | `fred`              |
| `series_item_key`      | Operator-facing series trigger identity                                 | `fred_gasregw`      |
| `canonical_series_key` | Persistence identity in the canonical observation store                 | `ENERGY.US.GASREGW` |
| `ownership_mode`       | Schedule authority: `grouped` (one schedule owns all series) or `split` | `grouped`           |

## Dataset Discovery API Expectations

Provider adapters that emit canonical records feed the backend dataset discovery APIs. To ensure data appears correctly in discovery/search/detail surfaces, keep the following guarantees:

- Discovery runtime responses are served from persisted records in the local stack; fixture-backed discovery payloads are reserved for automated tests only.

- Always emit stable canonical `series_key` values because backend detail lookup uses canonical identifiers.
- Emit `dataset_title`, `dataset_description`, and `dataset_geographic_scope` whenever known; these fields drive `/api/datasets/search` and `/api/datasets` matching.
- Emit `topic_tags` as `list[str]`; discovery search matches tag text and catalog/detail responses expose normalized tags.
- Preserve accurate `reported_at` timestamps; `/api/datasets/recent` ranking uses dataset recency derived from canonical observations.
- Keep per-series observations chronologically consistent so `/api/datasets/{dataset_id}` can return stable ordered points for chart rendering.
- Once canonical dataset records are ingested, frontend discovery surfaces will automatically show them: home search, recent updates feed, catalog list/grouping, and dataset detail pages.

---

## Step 1: Implement the Source Adapter

Create `apps/pipeline/src/orchestration/jobs/sources/<provider>_source.py`.

> **Naming is required**: the file must end in `_source.py` or dynamic discovery will skip it.

Required interface:

- Export a module-level constant `<PROVIDER>_SOURCE_KEY = "<provider>_source"` (or `"<provider>_<series>"` for multi-series grouped sources).
- Export a `build_<provider>_source_workflow(runner, ...)` function that returns `SourceWorkflowRegistration`.
- Export a module-level `SOURCE_SPEC` dictionary with all manifest fields consumed by discovery.
- Set `workflow_id` to a stable unique string (e.g. `"wf-<provider>-source"`).
- Support both trigger modes: `{"scheduled", "on_demand"}`.
- Return `SourceWorkflowResult` from the handler with clear counts.
- For multi-series providers: check `request.run_context.get("series_item_keys")` to filter which series to fetch that run. See `fred_fedfunds_source.py` for the canonical multi-series pattern.
- When emitting canonical records, include dataset metadata fields when available: `dataset_title`, `dataset_description`, and `dataset_geographic_scope`.
- Topic metadata must be emitted as `topic_tags: list[str]` (not comma-delimited strings). The persistence layer normalizes and de-duplicates tags before upserting `topic_tags` and `data_series_topic_tags`.

Minimal single-series skeleton:

```python
# apps/pipeline/src/orchestration/jobs/sources/acme_cpi_source.py
from __future__ import annotations
from ..source_ingest_runner import SourceIngestRunner
from ..source_schedule_policy import SourceSchedulePolicy
from ..workflow_registry import SourceWorkflowRegistration
from ..workflow_request import SourceWorkflowRequest
from ..workflow_result import SourceWorkflowResult

ACME_CPI_SOURCE_KEY = "acme_cpi"

def build_acme_cpi_source_workflow(
    runner: SourceIngestRunner,
    schedule_policy: SourceSchedulePolicy | None = None,
) -> SourceWorkflowRegistration:
    def _handler(request: SourceWorkflowRequest) -> SourceWorkflowResult:
        # fetch, normalize, and persist observations here
        records = [
            {
                "source_name": "ACME",
                "source_type": "external",
                "series_key": "PRICE.US.CPI",
                "metric_name": "Consumer Price Index",
                "dataset_title": "US Consumer Price Index",
                "dataset_description": "Monthly CPI for US urban consumers.",
                "dataset_geographic_scope": "United States",
                "topic_tags": ["inflation", "consumer prices"],
                "frequency": "monthly",
                "date": "2026-01-01",
                "reported_at": "2026-02-01T00:00:00Z",
                "value": "302.5",
            }
        ]
        return runner.run_records(request=request, records=records)

    return SourceWorkflowRegistration(
        workflow_id="wf-acme-cpi-source",
        source_key=ACME_CPI_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )
```

References:

- `apps/pipeline/src/orchestration/jobs/sources/example_source.py` (minimal single-series)
- `apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py` (multi-series with checkpoint)

---

## Step 2: Declare SOURCE_SPEC in the Adapter Module

Add `SOURCE_SPEC` in the same `*_source.py` module you created in Step 1.

```python
SOURCE_SPEC: dict[str, Any] = {
    "source_key": ACME_CPI_SOURCE_KEY,
    "provider_group_key": "acme",
    "series_item_keys": ("acme_cpi",),
    "canonical_series_keys": ("PRICE.US.CPI",),
    "ownership_mode": "grouped",
    "cron_schedule": "0 0 1 * *",
    "cadence_label": "monthly",
    "builder": build_acme_cpi_source_workflow,
}
```

Constraints:

- `series_item_keys` and `canonical_series_keys` must have equal length and matching index order.
- `source_key` must be unique across all adapter modules.
- `cron_schedule` must be valid five-field cron syntax.
- `cadence_label` must be one of: `hourly`, `daily`, `weekly`, `monthly`, `custom_interval`.
- Discovery ordering is deterministic by `source_key` (alphabetical).

---

## Step 3: Contract Validation (No Action — Automatic)

Once `SOURCE_SPEC` is present, discovery and contract guards run automatically at runtime startup and fail fast if:

- registration `status` is not `"active"`
- `workflow_id` is empty
- `source_key` is empty or a duplicate

No code changes needed here. Violations include module path, source key, and reason.

---

## Step 4: Verify Derived Schedules and Assets (No Bootstrap Edits)

Do not edit schedule/asset bootstrap files for provider onboarding. They are derived from discovered specs.

Each generated schedule will tag runs with:

```
trigger_type=scheduled
source_selection_mode=source_owned
source_keys=acme_cpi
provider_group_key=acme
series_item_keys=acme_cpi
cadence_label=monthly
```

For a multi-series grouped source, include all series item keys in `SOURCE_SPEC.series_item_keys` under one `source_key`. The schedule fires once and the handler filters which series to process per run.

---

## Step 5: Verify Derived Workspace Catalog (No Bootstrap Edits)

`definitions.py` derives workspace catalog values from generated assets and schedules. No manual catalog edits are required for provider onboarding.

---

## Step 6: Verify Locally

Run targeted orchestration checks:

```bash
# Dynamic registration, contract, and smoke tests
pnpm exec nx run pipeline:test:orchestration:dynamic-registration
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_single_file_onboarding_guard.py

# Full orchestration suite
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/

# Affected quality gates
pnpm run affected:lint
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Dagit verification:

```bash
# Start local Dagit and verify workspace loads
bash tools/quality/local-stack/start-dagit-local.sh
bash tools/quality/local-stack/test-dagit-endpoint.sh

# Confirm new asset keys are present in the loaded workspace
PYTHONPATH=apps/pipeline uv run --project apps/pipeline python -c \
  'from src.orchestration.definitions import defs; print("\n".join(sorted(k.to_user_string() for k in defs.resolve_all_asset_keys())))'
```

Expected results:

- Dagit endpoint returns `DAGIT_HEALTH_STATUS=ready`
- New provider assets appear in the catalog under the intended prefix (e.g. `acme/cpi`)
- Schedule appears in the Dagit Automation view as `acme_cpi_schedule`

---

## Step 8: Persistence and Migration Checks (When Schema Changes)

Only needed when the new source requires new runtime persistence fields or tables:

1. Add or update SQLAlchemy models in `libs/db/src/db/models/`
2. Add a new Alembic migration in `libs/db/alembic/versions/`
3. Run local migration and revision checks:
   ```bash
   bash tools/quality/local-stack/run-db-migrations.sh
   bash tools/quality/local-stack/check-db-revision.sh
   ```
4. Add migration and model regression tests under `libs/db/tests/`

---

## PR Checklist

Before opening a PR, confirm all of the following:

- [ ] Source adapter module file ends in `_source.py`
- [ ] `SourceBuilderSpec` added to `_build_default_specs()` in `discovery.py`
- [ ] `series_item_keys` and `canonical_series_keys` are equal length and index-aligned
- [ ] `source_key` is unique across all existing specs (no duplicates)
- [ ] Schedule cadence added to all four dicts in `source_asset_schedules.py`
- [ ] Dagit assets added to `source_asset_definitions.py` with correct `key_prefix`
- [ ] `WORKSPACE_DEFINITION_CATALOG` in `definitions.py` updated for new assets and schedule
- [ ] Key identities consistent: `source_key`, `provider_group_key`, `series_item_key`, `canonical_series_key`
- [ ] `grouped` vs `split` ownership decision is explicit in `SourceBuilderSpec.ownership_mode`
- [ ] `pnpm exec nx run pipeline:test:orchestration:dynamic-registration` passes
- [ ] Affected quality gates pass (`lint`, `typecheck`, `test`, `coverage`)
- [ ] Dagit endpoint returns ready and new assets are visible in catalog
- [ ] Runbook / docs updated if any new cadence patterns or naming conventions were introduced
