# Quickstart: Source Metadata and Adapter Relocation

## Prerequisites

- Workspace dependencies are installed.
- Local Docker Compose stack can be restarted cleanly.
- Existing maintained source adapters have been migrated into the new maintained source package.
- Database migration `0010_source_profile_metadata` has been applied locally.

## Implementation Validation Flow

1. Run focused pipeline tests for manifest validation, discovery, bootstrap generation, and affected source workflows.
2. Run focused DB and backend tests for schema/model/query/HTTP contracts that expose source metadata.
3. Run focused frontend tests for source list/detail routes, discovery client types, and shared source presentation components.
4. Restart the local stack cleanly and manually validate source bootstrap, ingest persistence, source APIs, and source pages.
5. Run `pre-commit run --all-files`.
6. Run mandatory monorepo-wide test and coverage stop gates before commit or handoff.

## Suggested Verification Commands

- Focused pipeline tests:
  - `uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py apps/pipeline/tests/orchestration/test_source_asset_discovery.py apps/pipeline/tests/orchestration/test_definitions_smoke.py apps/pipeline/tests/orchestration/test_fred_source_workflow.py apps/pipeline/tests/orchestration/test_eia_retail_fuel_prices_source_workflow.py apps/pipeline/tests/orchestration/test_nyfed_college_labor_market_source_workflow.py`
  - `uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/integration/test_provider_bootstrap_cli_success.py apps/pipeline/tests/integration/test_provider_bootstrap_cli_invalid_input.py apps/pipeline/tests/integration/test_provider_bootstrap_cli_collisions.py`
  - `uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/contract/test_provider_bootstrap_scaffold_contract.py apps/pipeline/tests/contract/test_onboard_provider_skill_bootstrap_standard.py apps/pipeline/tests/contract/test_provider_onboarding_runbook_standard.py`
- Focused DB/backend tests:
  - `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_source_list_query_contract.py apps/backend/tests/contract/test_source_detail_query_contract.py apps/backend/tests/contract/test_http_runtime_source_endpoints.py`
  - `uv run --project libs/db pytest --no-cov libs/db/tests/test_models_foundation.py libs/db/tests/test_ingestion_runtime_migrations.py`
- Frontend tests:
  - `pnpm --dir apps/frontend test source-list-page.test.tsx source-detail-page.test.tsx discovery-types.test.ts source-discovery-client.test.ts shell-structure-contract.test.tsx`
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Final gates:
  - `pre-commit run --all-files`
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Manual Validation Checklist

- Cleanly restart the local environment before manual verification:
  - `docker compose down`
  - `docker compose up -d`
- Generate a new adapter scaffold with the standard bootstrap command and confirm the file is created under `apps/pipeline/src/sources`.
- Example bootstrap validation command:
  - `pnpm run provider:bootstrap -- --provider-group-key demo --source-key demo_prices --module-name demo_prices_source --cadence-label monthly --cron-schedule "0 0 1 * *" --series-item-key demo_prices --canonical-series-key PRICE.US.DEMO --provider-series-id DEMO001 --source-title "Demo Prices" --source-description "Monthly demo price series."`
- Confirm bootstrap validation rejects missing source title or source description inputs.
- Start the pipeline runtime and confirm all maintained adapters are discovered from the new source package.
- Run at least one migrated source ingest path and confirm source-level persistence records include stable source identity, source title, and source description.
- Query source list and source detail endpoints and confirm payloads use stable source identifiers plus human-readable source title and description.
- Open `/sources` and at least two `/sources/{sourceId}` routes and confirm:
  - source titles are the primary labels
  - source descriptions are visible in source context
  - dataset membership remains correct
  - unknown routes still render not-found behavior
- Review onboarding runbook and onboarding skill guidance and confirm both point contributors to the new source package and metadata requirements.

## Completion Criteria

- Maintained adapters are discoverable from the new source package only.
- Source manifests without title or description fail validation.
- Persisted source profiles expose populated source title and description for maintained sources.
- Backend and frontend source discovery flows use stable source identifiers with human-readable source metadata.
- All required automated checks, manual validation steps, and monorepo stop gates pass.
