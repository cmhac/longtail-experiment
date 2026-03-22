# Local Stack Baseline Runbook

## Start

1. Run docker compose up -d
2. Run docker compose ps
3. Optional: verify DB bootstrap only with bash tools/quality/local-stack/test-local-db-bootstrap.sh

## Healthy State

- pipeline service is listed and healthy.
- backend service is listed and healthy.
- frontend service is listed and healthy.
- db service is listed and healthy.

## Local DB Persistence Policy

- The local DB is persistent by default using the `local_db_data` volume.
- Do not reset the DB during normal development loops.
- Use explicit reset only when you intentionally need a clean database baseline:
  1.  Run `docker compose down -v`
  2.  Run `docker compose up -d db`

## Troubleshooting

- If backend is unhealthy, inspect: docker compose logs backend
- If frontend is unhealthy, inspect: docker compose logs frontend
- If pipeline is unhealthy, inspect: docker compose logs pipeline
- If db is unhealthy, inspect: docker compose logs db
- If any service fails health checks, stop stack with docker compose down and fix configuration before retry.
- If migrations fail with role/auth errors on port 5432, verify local defaults from `docker/compose/stack.env` and ensure commands target `LOCAL_DB_PORT=55432`.
- If migration or revision scripts fail while DB is stopped, rerun the same command; scripts now auto-start `db` and then wait for healthy status.

## Contract Verification After Startup

1. Run pipeline contract tests: `uv run --project apps/pipeline pytest apps/pipeline/tests/contract`
2. Run backend contract tests: `uv run --project apps/backend pytest apps/backend/tests/contract`
3. Apply shared DB migrations: `bash tools/quality/local-stack/run-db-migrations.sh`
4. Verify revision baseline: `bash tools/quality/local-stack/check-db-revision.sh`
5. Run end-to-end readiness helper: `bash tools/quality/local-stack/test-db-readiness.sh`
6. Verify quality gates for affected changes:
   - `pnpm run affected:lint`
   - `pnpm run affected:test`
   - `pnpm run affected:coverage`

## Development-only Warning

- Local DB migration scripts are for local development environments only.
- Do not run these commands against non-development databases.

## Contract-Specific Troubleshooting

- If canonical validation tests fail, inspect `apps/pipeline/src/contract/schemas/canonical_observation.py` and `apps/pipeline/src/contract/normalizers/source_payload_mapper.py`.
- If provenance/revision audit tests fail, inspect `apps/pipeline/src/contract/services/revision_lineage_service.py` and `apps/backend/src/contract/query/provenance_audit_query.py`.
- If hierarchy filter tests fail, inspect `apps/pipeline/src/contract/services/taxonomy_mapping_service.py` and `apps/backend/src/contract/query/hierarchy_query.py`.

## Source Workflow Onboarding

1. Add a new source adapter under `apps/pipeline/src/orchestration/jobs/sources/`.
2. Build a `SourceWorkflowRegistration` using `build_example_source_workflow` as the reference pattern.
3. Register the workflow in orchestration bootstrap wiring before execution.
4. Validate onboarding behavior with:

- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_workflow_contract.py`
- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_onboarding_flow.py`

## Bounded Parallel Ingestion Validation (Feature 006)

1. Run cadence eligibility verification:

- `nx run pipeline:test:orchestration:cadence`

2. Run bounded concurrency verification:

- `nx run pipeline:test:orchestration:parallel`

3. Run full orchestration suite if either command fails:

- `nx run pipeline:test:orchestration`

Expected operator signals:

- Deferred sources are recorded when due work exceeds configured active-source capacity.
- Not-due and invalid-policy sources are excluded from scheduled execution with explicit reasons.

## Schedule State Inspection and Reset (Feature 007)

Use these SQL helpers to inspect and control schedule persistence in local troubleshooting loops.

1. Inspect persisted schedule state:
   `SELECT source_key, cadence_type, last_successful_at, updated_at FROM source_schedule_policies ORDER BY source_key;`
2. Force one source to become due by backdating last success:
   `UPDATE source_schedule_policies SET last_successful_at = NOW() - INTERVAL '2 days' WHERE source_key = 'fred_fedfunds';`
3. Hard reset schedule state for all sources:
   `DELETE FROM source_schedule_policies;`

After changing schedule state manually, trigger a new run and confirm eligibility outcomes in
`source_eligibility_snapshots` for the latest `run_id`.
