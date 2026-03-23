# Local Stack Baseline Runbook

## Start

1. Run docker compose up -d
2. Run docker compose ps
3. Optional: verify DB bootstrap only with bash tools/quality/local-stack/test-local-db-bootstrap.sh

## Dagit Local Workflow (Feature 009)

Dagit is available as a Docker Compose service in this stack. Use these helpers from repository root to run and verify the local orchestration UI.

0. Start stack services (includes Dagit):
   - `docker compose up -d`

1. Start Dagit:
   - `bash tools/quality/local-stack/start-dagit-local.sh`
2. Verify endpoint and workspace load:
   - `bash tools/quality/local-stack/test-dagit-endpoint.sh`
3. Stop Dagit:
   - `bash tools/quality/local-stack/stop-dagit-local.sh`

If startup or verification fails, inspect the `DAGIT_FAILURE_CATEGORY` output:

- `prerequisite_missing`: missing local prerequisites or wrong command context.
- `endpoint_unavailable`: process started but endpoint is unreachable.
- `workspace_load_failed`: UI endpoint responds but workspace definitions are not loaded.
- `partial_environment`: startup failed due to incomplete local runtime context.

### Dagit Failure Matrix

| Failure Category        | Observable Symptom                                  | Likely Root Cause                                                         | Recovery Steps                                                                     | Verification Step                                                                           |
| ----------------------- | --------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `prerequisite_missing`  | Helper exits immediately before endpoint probe      | Missing `uv`, wrong working directory, or incomplete dependency setup     | Install prerequisites, switch to repository root, rerun startup helper             | `bash tools/quality/local-stack/start-dagit-local.sh` returns `DAGIT_START_STATUS=ready`    |
| `endpoint_unavailable`  | Startup reports running but endpoint check fails    | Port conflict, webserver startup failure, or process crash                | Stop conflicting process, inspect `.tmp/dagit-local.log`, restart helper           | `bash tools/quality/local-stack/test-dagit-endpoint.sh` returns `DAGIT_HEALTH_STATUS=ready` |
| `workspace_load_failed` | Endpoint reachable but workspace verification fails | Definitions module load error or empty workspace location entries         | Validate `src.orchestration.definitions` imports and runtime wiring, restart Dagit | `DAGIT_VERIFY_WORKSPACE=1 bash tools/quality/local-stack/test-dagit-endpoint.sh` passes     |
| `partial_environment`   | Startup helper emits fallback degraded category     | Mixed env state, stale pid/log state, or partial local stack availability | Run stop helper, clear stale state, ensure compose stack healthy, restart          | Stop/start cycle and endpoint probe both succeed                                            |

## Healthy State

- pipeline service is listed and healthy.
- backend service is listed and healthy.
- frontend service is listed and healthy.
- dagit service is listed and healthy.
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
3. Register the adapter via discovery specs in `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`
4. Validate onboarding behavior with:

- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_workflow_contract.py`
- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_onboarding_flow.py`
- `pnpm exec nx run pipeline:test:orchestration:dynamic-registration`

## Source-Asset Cutover Operations (Feature 010)

1. Validate source-asset discovery and contract guards:

- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_asset_discovery.py`
- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py`

2. Validate source-targeted manual triggers and invalid-key fail-fast behavior:

- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_single_source_trigger_runtime.py`

3. Validate source-level visibility and post-cutover persistence:

- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_outcome_visibility.py`
- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_outcome_persistence_post_cutover.py`

4. Validate Dagster-only authority and partial-failure recovery posture:

- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_scheduler_runtime.py`
- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_cutover_partial_failure_behavior.py`

Operator expectation after cutover:

- Legacy non-Dagster scheduling paths remain disabled.
- Source failures produce source-level failure summaries without scheduler fallback.

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

## Per-Source Schedule Cutover Verification (Feature 011)

1. Verify no shared all-source schedule exists:
   `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_definitions_smoke.py -k "no_shared"`

2. Verify per-source schedules are registered:
   `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_definitions_smoke.py -k "per_source_schedules"`

3. Verify trigger attribution for source-owned schedules:
   `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_trigger_modes.py -k "source_schedule_trigger"`

4. Verify historical artifact non-authority:
   `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_run_visibility_audit.py -k "historical_artifacts"`

5. Apply cutover migration and verify:
   `bash tools/quality/local-stack/run-db-migrations.sh`
   `bash tools/quality/local-stack/check-db-revision.sh`

6. Full orchestration test suite:
   `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration --no-cov`

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

## Feature Gap Triage and Escalation (Feature 008)

Use this when implementation reveals a blocker that prevents expected FRED ingest behavior.

1. Confirm the blocker is reproducible with one exact command and one exact failure signal.
2. Add or update a row in `specs/008-add-fred-source/spec.md` under the Gap Log table.
3. Update `specs/008-add-fred-source/plan.md` if architecture, migration, or contract scope changes.
4. Add corresponding test and implementation tasks in `specs/008-add-fred-source/tasks.md`.
5. Escalate to the feature owner if the blocker affects migration safety, contract integrity,
   or local-stack runability.

Escalation package must include:

- Failing command and abbreviated output
- Reproduction preconditions (env vars, migration head, trigger type)
- Proposed owner and resolution target
- Deferral rationale if immediate fix is not possible

Feature 008 implementation delta (resolved):

- Symptom: `column "series_key" does not exist` while reading observations.
- Cause: repository query expected `observations.series_key`, but contract schema uses
  `observations.series_id` with `data_series.series_key` join.
- Resolution: use repository code that writes/reads through
  `source_profiles` -> `data_series` -> `observations(series_id)` and query series key via join.

## Grouped-vs-Split Adapter Operations (Feature 012)

Use this decision table before onboarding new provider series:

- Keep grouped ownership when:
  - Cadence requirements are shared.
  - Operational trigger isolation is not required beyond series-level on-demand runs.
- Use split ownership when:
  - A series requires materially different cadence.
  - Operational risk requires separate schedule authority for one series.

Ownership transition guardrails:

1. Define one effective ownership boundary timestamp for the moving series.
2. Disable old schedule authority before enabling new authority.
3. Validate no duplicate scheduled run for the same series_item_key in the same cadence window.
4. Verify run attribution remains explicit after transition.

Verification commands:

- `pnpm exec nx run pipeline:test:orchestration:multi-series`
- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_trigger_modes.py -k "grouped or split or ownership_transition"`
- `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_outcome_visibility.py`
