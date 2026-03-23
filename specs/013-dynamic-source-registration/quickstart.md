# Quickstart: Dynamic Source Workflow Registration

## Objective

Validate that source workflow registration is discovery-driven, deterministic, and contract-safe while preserving existing source behavior.

## Prerequisites

- Repository dependencies installed.
- Local compose services available.
- Feature branch `013-dynamic-source-registration` checked out.

## 1) Run discovery and contract validation tests

```bash
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_source_asset_discovery.py
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py
```

Expected:

- Valid adapters are discovered.
- Non-adapter modules are ignored per policy.
- Malformed adapters fail with actionable diagnostics.
- Duplicate source-key paths are rejected.

## 2) Run orchestration smoke coverage for registered sources

```bash
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_definitions_smoke.py
```

Expected:

- Runtime wiring and workspace load checks pass.
- Registered source expectations remain valid without hard-coded runtime bootstrap imports.

## 3) Verify local Dagit endpoint and workspace

```bash
bash tools/quality/local-stack/start-dagit-local.sh
bash tools/quality/local-stack/test-dagit-endpoint.sh
```

Expected:

- `DAGIT_START_STATUS=ready`
- `DAGIT_HEALTH_STATUS=ready`
- Workspace location entries are loaded.

## 4) Execute affected quality gates

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Expected:

- All affected gates pass with no suppression/bypass changes.
- Coverage remains at or above repository thresholds.

## 5) Verify onboarding documentation flow

- Confirm source onboarding guidance no longer requires manual runtime bootstrap edits.
- Confirm runbook onboarding steps match discovery-based registration behavior.

## Acceptance Evidence Checklist

- New compliant adapter onboarding requires no runtime bootstrap file edits.
- Registration order is deterministic across repeated runs.
- Malformed/duplicate adapter startup failures are actionable and module-scoped.
- Existing adapters continue to register and execute successfully.

## Execution Evidence (2026-03-22)

Validation commands executed:

- `pnpm exec nx run pipeline:test:orchestration:dynamic-registration`
  - Result: `23 passed in 1.31s`
- `pnpm run affected:lint`
  - Result: passed
- `pnpm run affected:format`
  - Result: passed
- `pnpm run affected:typecheck`
  - Result: passed
- `pnpm run affected:test`
  - Result: passed
- `pnpm run affected:coverage`
  - Result: passed

Dagit runtime checks:

- `bash tools/quality/local-stack/test-compose-stack.sh`
  - Result: local stack health checks passed; compose services started healthy and were torn down cleanly
- `bash tools/quality/local-stack/start-dagit-local.sh`
  - Result: `DAGIT_START_STATUS=ready`
- `bash tools/quality/local-stack/test-dagit-endpoint.sh`
  - Result: `DAGIT_HEALTH_STATUS=ready`, `DAGIT_LOCATION_ENTRIES=1`
- `PYTHONPATH=apps/pipeline uv run --project apps/pipeline python -c 'from src.orchestration.definitions import defs; print("\\n".join(sorted(k.to_user_string() for k in defs.resolve_all_asset_keys())))'`
  - Result asset keys:
    - `fred/fedfunds`
    - `fred/gasregw`
    - `test/dummy_source`
    - `test/example_source`

Browser validation notes:

- Dagit UI opened at `http://127.0.0.1:3001` and navigation sections loaded (`Catalog`, `Lineage`, `Deployment`).
- Deployment > Code locations shows `src.orchestration.definitions` with `Loaded` status.
- Catalog > Assets displays slash-prefix dynamic assets: `fred/fedfunds`, `fred/gasregw`, `test/dummy_source`, and `test/example_source`.
