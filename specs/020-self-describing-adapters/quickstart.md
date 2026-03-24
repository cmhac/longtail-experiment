# Quickstart: Onboarding a New Source (Feature 020 Model)

**After feature 020 is complete, this is the complete onboarding procedure.**

---

## Prerequisites

- Local dev stack running: `docker compose up -d`
- Pipeline virtualenv active: `uv sync --project apps/pipeline --frozen`
- Migrations up to date: `bash tools/quality/local-stack/run-db-migrations.sh`

---

## Step 1 — Create the adapter module (the ONLY step)

Create one file:

```
apps/pipeline/src/orchestration/jobs/sources/{provider}_{dataset}_source.py
```

The file must export a `SOURCE_SPEC: SourceBuilderSpec` at module level.
See [contracts/adapter-manifest-contract.md](contracts/adapter-manifest-contract.md) for
the full field specification and a minimal working example.

**Key fields to fill in:**

```python
SOURCE_SPEC = SourceBuilderSpec(
    source_key="myprovider_mydataset",
    module_name="src.orchestration.jobs.sources.myprovider_mydataset_source",
    builder=lambda runner, obs_repo: build_myprovider_workflow(runner, observation_repository=obs_repo),
    provider_group_key="myprovider",
    series_item_keys=("myprovider_seriesA", "myprovider_seriesB"),
    canonical_series_keys=("CATEGORY.US.SERIESA", "CATEGORY.US.SERIESB"),
    ownership_mode="grouped",
    cron_schedule="0 6 * * 1",   # e.g. weekly Mondays 06:00 UTC
    cadence_label="weekly",
)
```

---

## Step 2 — Verify (no code edits required)

Restart the pipeline and check the Dagit operator UI. The new source should appear
automatically as:

- A registered entry in the source catalog.
- A schedule named `{source_key}_schedule` running at the declared cron.
- One `@asset` per declared series item under the `{provider_group_key}/` key prefix.

**Quick smoke check** (without a running Dagit):

```bash
uv run --project apps/pipeline python - <<'EOF'
from src.orchestration.jobs.source_assets.discovery import scan_adapter_modules
for spec in scan_adapter_modules():
    print(f"  {spec.source_key}  ·  series={spec.series_item_keys}  ·  cron={spec.cron_schedule}")
EOF
```

---

## Step 3 — Run quality gates

```bash
# Adapter-level quality checks
uv run --project apps/pipeline ruff check apps/pipeline
uv run --project apps/pipeline ruff format --check apps/pipeline
uv run --project apps/pipeline ty check apps/pipeline

# Full test suite (mandatory stop gate)
pnpm exec nx run-many -t test --all
pnpm exec nx run-many -t coverage --all
```

All tests must pass. No other files need editing for a conforming adapter.

---

## What the runtime does automatically when your adapter is on disk

1. **`scan_adapter_modules()`** finds `*_source.py`, imports your module, and reads
   `SOURCE_SPEC`. Validates against all manifest rules and halts startup on violation.
2. **`SOURCE_ASSET_SCHEDULES`** in `source_asset_schedules.py` includes a Dagster
   schedule built from your `cron_schedule` and `cadence_label` fields.
3. **`SOURCE_DAGIT_ASSETS`** in `source_asset_definitions.py` includes one `@asset`
   per `series_item_key`, keyed as `{provider_group_key}/{series_name}`.
4. **`WORKSPACE_DEFINITION_CATALOG`** in `definitions.py` reflects your assets and
   schedule in the smoke-test catalog.
5. **`EXPECTED_RUNTIME_SOURCE_KEYS`** in `runtime.py` includes your `source_key` in
   the Dagit wiring verification check.

---

## Troubleshooting

| Symptom                                                             | Likely cause                                                 | Fix                                                              |
| ------------------------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------- |
| `SourceAdapterManifestError: missing required field: cron_schedule` | Forgot `cron_schedule` in `SOURCE_SPEC`                      | Add `cron_schedule="..."`                                        |
| `SourceAdapterManifestError: duplicate source_key`                  | Two adapters share the same `source_key`                     | Use a unique `source_key`                                        |
| Source not appearing in Dagit                                       | Module not ending in `_source.py`                            | Rename file to `{provider}_{dataset}_source.py`                  |
| Asset key wrong in Dagit                                            | `series_item_key` doesn't start with `{provider_group_key}_` | Convention: `{provider_group_key}_{name}` (e.g. `fred_fedfunds`) |
| `missing attribute SOURCE_SPEC`                                     | Forgot to export `SOURCE_SPEC`                               | Add the module-level `SOURCE_SPEC = SourceBuilderSpec(...)`      |
