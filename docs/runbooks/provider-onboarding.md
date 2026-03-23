# Provider Onboarding Runbook

This guide captures the current repository workflow for adding a new ingestion provider (or adding new series under an existing provider) to the Dagster orchestration runtime.

## Architecture Snapshot

Provider onboarding in this codebase has four linked surfaces:

1. Source workflow adapter (provider integration and mapping)
2. Runtime discovery and registration (provider metadata + contract checks)
3. Schedule metadata and trigger tags (per-source cadence)
4. Dagit assets (operator visibility and manual materialization)

A provider is considered onboarded only when all four surfaces are updated and verified.

## Data Model Terms

Use these keys consistently:

- `source_key`: workflow registration and schedule identity (for example, `fred_fedfunds`)
- `provider_group_key`: grouping identity for related series (for example, `fred`)
- `series_item_key`: operator-facing series trigger identity (for example, `fred_gasregw`)
- `canonical_series_key`: persistence identity used by the canonical observation store
- `ownership_mode`: grouped or split schedule ownership per series item

## Step 1: Implement Source Adapter

Add a source module under `apps/pipeline/src/orchestration/jobs/sources/` following the existing adapter pattern.

Required behavior:

- Export a `build_<provider>_source_workflow(...)` function that returns `SourceWorkflowRegistration`
- Support both trigger modes: `scheduled` and `on_demand` unless there is a strong reason not to
- Return `SourceWorkflowResult` with clear counts and optional `series_outcomes` for multi-series providers
- Use `request.run_context["series_item_keys"]` filtering for series-targeted runs
- Use stable `outcome_reason_code` values for failures

Implementation references:

- `apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py`
- `apps/pipeline/src/orchestration/jobs/workflow_result.py`

## Step 2: Register Provider in Discovery Specs

Update `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`.

Add or modify a `SourceBuilderSpec` entry in `_build_default_specs()`:

- `source_key`
- `module_name`
- `builder`
- `provider_group_key`
- `series_item_keys`
- `canonical_series_keys`
- `ownership_mode` (`grouped` by default; use `split` when cadence/operational authority diverges)

Important constraints:

- `series_item_keys` and `canonical_series_keys` must have matching lengths
- `source_key` values must be unique across all specs
- Discovery order is deterministic by `source_key`

## Step 3: Keep Contract Validation Green

Discovery results are validated before registration in:

- `apps/pipeline/src/orchestration/jobs/source_assets/contracts.py`

Registration will fail fast when:

- registration status is not active
- `source_key` is empty
- `workflow_id` is empty
- duplicate `source_key` values exist across discovered modules

## Step 4: Configure Per-Source Cadence + Trigger Tags

Update `apps/pipeline/src/orchestration/schedules/source_asset_schedules.py`:

- Add `source_key` cadence in `SOURCE_CADENCE_DEFINITIONS`
- Add `series_item_keys` in `SOURCE_SERIES_ITEM_DEFINITIONS`
- Add `provider_group_key` in `SOURCE_PROVIDER_GROUP_DEFINITIONS`
- Add schedule definition in `SOURCE_ASSET_SCHEDULES`

Expected schedule tags include:

- `trigger_type=scheduled`
- `source_selection_mode=source_owned`
- `source_keys=<source_key>`
- `provider_group_key=<provider_group_key>`
- `series_item_keys=<comma-separated series_item_keys>`

## Step 5: Expose Dagit Assets with Key Prefixes

Update `apps/pipeline/src/orchestration/source_asset_definitions.py`.

Asset key guidance:

- Use `key_prefix` for logical grouping in Dagit
- Current convention examples:
  - `key_prefix="fred"` + `name="fedfunds"` -> `fred/fedfunds`
  - `key_prefix="test"` + `name="dummy_source"` -> `test/dummy_source`

Execution guidance:

- Keep `source_key` and `series_item_key` values aligned with runtime registration identities
- For grouped providers, run series-item assets through the grouped `source_key` while passing the selected `series_item_key`

## Step 6: Update Definitions Catalog Expectations

Update `apps/pipeline/src/orchestration/definitions.py` `WORKSPACE_DEFINITION_CATALOG` entries so smoke checks match live Dagster keys.

## Step 7: Verify Locally

Run targeted orchestration checks:

```bash
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_source_asset_discovery.py
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_definitions_smoke.py
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_trigger_modes.py -k "source_schedule_trigger or grouped or split or ownership_transition"
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_series_selection.py
```

Dagit verification:

```bash
bash tools/quality/local-stack/start-dagit-local.sh
bash tools/quality/local-stack/test-dagit-endpoint.sh
PYTHONPATH=apps/pipeline uv run --project apps/pipeline python -c 'from src.orchestration.definitions import defs; print("\\n".join(sorted(k.to_user_string() for k in defs.resolve_all_asset_keys())))'
```

Expected result:

- Dagit endpoint returns ready
- workspace loads successfully
- new provider assets appear with intended prefix grouping

## Step 8: Persistence + Migration Checks (When Schema Changes)

If onboarding adds runtime persistence fields/tables:

1. Add/adjust SQLAlchemy models in `libs/db/src/db/models/`
2. Add Alembic migration in `libs/db/alembic/versions/`
3. Run local migration scripts and revision checks
4. Add migration/model regression tests under `libs/db/tests/`

## PR Checklist

Before opening a PR, confirm:

- adapter, discovery, schedules, and Dagit assets are all updated
- key identities are consistent (`source_key`, `provider_group_key`, `series_item_key`, `canonical_series_key`)
- grouped vs split ownership decision is explicit and tested
- targeted orchestration tests pass
- Dagit endpoint/workspace checks pass
- docs and runbook notes are updated for operator visibility
