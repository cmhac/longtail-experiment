# Provider Onboarding Runbook

This guide covers the end-to-end process for adding a new ingestion provider (or new series under an existing provider) to the Dagster orchestration runtime.

## What Is and Isn't Automated

**Automatically handled by dynamic registration** (no bootstrap edits required):

- Runtime workflow registration — adding a `SourceBuilderSpec` to `_build_default_specs()` is the only step needed for the runtime to discover and register the source. No changes to `runtime.py` are needed.
- Duplicate source-key detection — the contract guard will fail fast at startup if `source_key` collides.
- Deterministic registration ordering — discovery sorts by `source_key`; startup order is stable.

> **Naming constraint**: The source module filename **must end in `_source.py`** (e.g. `acme_cpi_source.py`). The `is_adapter_spec()` filter in `discovery.py` enforces this to avoid accidentally including helper or utility modules in adapter discovery.

**Still requires explicit code additions** for each new provider:

| Surface                                | File                                                                  | Required                 |
| -------------------------------------- | --------------------------------------------------------------------- | ------------------------ |
| Source adapter implementation          | `apps/pipeline/src/orchestration/jobs/sources/<provider>_source.py`   | Always                   |
| Discovery spec registration            | `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`     | Always                   |
| Schedule cadence + trigger tags        | `apps/pipeline/src/orchestration/schedules/source_asset_schedules.py` | Always                   |
| Dagit asset definitions                | `apps/pipeline/src/orchestration/source_asset_definitions.py`         | Always                   |
| Definitions catalog smoke expectations | `apps/pipeline/src/orchestration/definitions.py`                      | Always                   |
| DB model + Alembic migration           | `libs/db/src/db/models/`, `libs/db/alembic/versions/`                 | Only when schema changes |

## Data Model Terms

Use these keys consistently throughout all files:

| Term                   | Meaning                                                                 | Example             |
| ---------------------- | ----------------------------------------------------------------------- | ------------------- |
| `source_key`           | Workflow registration and schedule identity                             | `fred_fedfunds`     |
| `provider_group_key`   | Grouping key for related series sharing a provider                      | `fred`              |
| `series_item_key`      | Operator-facing series trigger identity                                 | `fred_gasregw`      |
| `canonical_series_key` | Persistence identity in the canonical observation store                 | `ENERGY.US.GASREGW` |
| `ownership_mode`       | Schedule authority: `grouped` (one schedule owns all series) or `split` | `grouped`           |

---

## Step 1: Implement the Source Adapter

Create `apps/pipeline/src/orchestration/jobs/sources/<provider>_source.py`.

> **Naming is required**: the file must end in `_source.py` or dynamic discovery will skip it.

Required interface:

- Export a module-level constant `<PROVIDER>_SOURCE_KEY = "<provider>_source"` (or `"<provider>_<series>"` for multi-series grouped sources).
- Export a `build_<provider>_source_workflow(runner, ...)` function that returns `SourceWorkflowRegistration`.
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

## Step 2: Register in the Discovery Spec Catalog

Edit `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`.

Add an import for your new source constants and builder at the top of the file alongside the existing imports, then add a `SourceBuilderSpec` entry to `_build_default_specs()`.

**This is the only step required for dynamic runtime registration.** No changes to `runtime.py` or any other bootstrap file are needed.

```python
# In _build_default_specs() — add after the existing entries:
SourceBuilderSpec(
    source_key=ACME_CPI_SOURCE_KEY,
    module_name="src.orchestration.jobs.sources.acme_cpi_source",
    builder=lambda runner, observation_repository: build_acme_cpi_source_workflow(
        runner,
        schedule_policy=SourceSchedulePolicy(
            source_key=ACME_CPI_SOURCE_KEY,
            cadence_type="monthly",
        ),
    ),
    provider_group_key="acme",
    series_item_keys=("acme_cpi",),
    canonical_series_keys=("PRICE.US.CPI",),
    # ownership_mode defaults to "grouped"; use "split" only when series
    # have independent cadence or operational ownership.
),
```

Constraints:

- `series_item_keys` and `canonical_series_keys` must have equal length and matching index order.
- `source_key` must be unique across all specs — the contract guard will raise at startup if not.
- Discovery ordering is deterministic by `source_key` (alphabetical). No manual ordering is needed.

---

## Step 3: Contract Validation (No Action — Automatic)

Once an entry is in `_build_default_specs()`, the contract guard in `apps/pipeline/src/orchestration/jobs/source_assets/contracts.py` runs automatically at runtime startup and will fail fast if:

- registration `status` is not `"active"`
- `workflow_id` is empty
- `source_key` is empty or a duplicate

No code changes needed here. If a contract violation occurs, the error message will name the module path from `SourceBuilderSpec.module_name`.

---

## Step 4: Configure Schedule Cadence and Trigger Tags

Edit `apps/pipeline/src/orchestration/schedules/source_asset_schedules.py`.

Add entries to each of the four configuration dictionaries and append a schedule object to `SOURCE_ASSET_SCHEDULES`:

```python
# 1. Cron schedule + human cadence label
SOURCE_CADENCE_DEFINITIONS: dict[str, tuple[str, str]] = {
    ...
    "acme_cpi": ("0 0 1 * *", "monthly"),  # first of each month at midnight
}

# 2. Series items triggered by this source's schedule
SOURCE_SERIES_ITEM_DEFINITIONS: dict[str, tuple[str, ...]] = {
    ...
    "acme_cpi": ("acme_cpi",),  # add multiple entries for multi-series grouped sources
}

# 3. Provider group key for run tag routing
SOURCE_PROVIDER_GROUP_DEFINITIONS: dict[str, str] = {
    ...
    "acme_cpi": "acme",
}

# 4. Build and register the schedule object (add near the bottom of the file)
acme_cpi_schedule = _make_source_schedule("acme_cpi", "0 0 1 * *", "monthly")

SOURCE_ASSET_SCHEDULES = [
    ...
    acme_cpi_schedule,
]
```

Each generated schedule will tag runs with:

```
trigger_type=scheduled
source_selection_mode=source_owned
source_keys=acme_cpi
provider_group_key=acme
series_item_keys=acme_cpi
cadence_label=monthly
```

For a multi-series grouped source (like `fred_fedfunds` which covers both `fred_fedfunds` and `fred_gasregw`), put all series item keys in `SOURCE_SERIES_ITEM_DEFINITIONS` under the single `source_key`. The schedule fires once and the handler filters which series to process per run.

---

## Step 5: Add Dagit Asset Definitions

Edit `apps/pipeline/src/orchestration/source_asset_definitions.py`.

Add one `@asset` per operator-visible series and append each to `SOURCE_DAGIT_ASSETS`.

Asset key naming convention: use `key_prefix` for the provider group and `name` for the series identifier. The Dagit asset key becomes `<key_prefix>/<name>`.

```python
# Single-series source:
@asset(name="cpi", key_prefix="acme", required_resource_keys={"run_coordinator"})
def acme_cpi_source_asset(context) -> dict[str, Any]:
    """Materialize source visibility entry for acme_cpi."""
    return _run_single_source(context=context, source_key="acme_cpi")

SOURCE_DAGIT_ASSETS = [
    ...
    acme_cpi_source_asset,
]
```

For a multi-series grouped source, add one `@asset` per series item and use `_run_series_item` instead of `_run_single_source`:

```python
# Multi-series source — one asset per series_item_key:
@asset(name="cpi", key_prefix="acme", required_resource_keys={"run_coordinator"})
def acme_cpi_asset(context) -> dict[str, Any]:
    """Materialize acme cpi series."""
    return _run_series_item(context=context, source_key="acme_cpi", series_item_key="acme_cpi")

@asset(name="ppi", key_prefix="acme", required_resource_keys={"run_coordinator"})
def acme_ppi_asset(context) -> dict[str, Any]:
    """Materialize acme ppi series."""
    return _run_series_item(context=context, source_key="acme_cpi", series_item_key="acme_ppi")
```

Conventions:

- `key_prefix` must match `provider_group_key` from the discovery spec.
- `source_key` passed to `_run_single_source` / `_run_series_item` must match the `source_key` in the discovery spec.
- `series_item_key` must be a member of `series_item_keys` from the discovery spec.

---

## Step 6: Update the Definitions Catalog

Edit `apps/pipeline/src/orchestration/definitions.py`.

Update `WORKSPACE_DEFINITION_CATALOG` to include the new asset keys and schedule name. This dictionary drives smoke tests that verify the live workspace matches expected definitions.

```python
WORKSPACE_DEFINITION_CATALOG: dict[str, tuple[str, ...]] = {
    "jobs": ("ingest_job",),
    "assets": (
        ...,
        "acme/cpi",                 # key_prefix/name from Step 5
    ),
    "schedules": (
        ...,
        "acme_cpi_schedule",        # name from Step 4
    ),
    "sensors": ("ondemand_sensor",),
}
```

---

## Step 7: Verify Locally

Run targeted orchestration checks:

```bash
# Dynamic registration, contract, and smoke tests
pnpm exec nx run pipeline:test:orchestration:dynamic-registration

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
