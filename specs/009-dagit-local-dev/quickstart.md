# Quickstart: Local Dagit Access

**Feature**: 009-dagit-local-dev  
**Goal**: Start Dagit locally and verify existing orchestration definitions are visible in the UI.

## Prerequisites

1. Repository dependencies are installed and synced.
2. Local stack services required by orchestration definitions are healthy.
3. Developer is running commands from repository root.

## Step 1: Prepare local environment

1. Ensure local development prerequisites from project onboarding are complete.
2. Start local stack dependencies if not already running.
3. Confirm migration/runtime baseline checks pass if required by current orchestration definitions.

## Step 2: Start Dagit locally

1. Run the startup helper from repository root:
   - `bash tools/quality/local-stack/start-dagit-local.sh`
2. Wait for readiness output indicating the UI endpoint is available.
3. If startup fails, capture the failure category and proceed to troubleshooting.

## Step 3: Open UI and verify workspace load

1. Open the local Dagit endpoint in a browser.
2. Confirm the landing page loads without blocking errors.
3. Confirm existing repository definitions appear in at least one listing view.
4. Run endpoint and workspace verification:
   - `DAGIT_VERIFY_WORKSPACE=1 DAGIT_MIN_LOCATION_ENTRIES=1 bash tools/quality/local-stack/test-dagit-endpoint.sh`

## Step 4: Verify definition details

1. Open one visible definition from the listing page.
2. Confirm detail view loads and displays expected metadata.
3. Record verification outcome as pass/fail.
4. Confirm `ingest_job` is present as a navigable definition detail page.

## Step 5: Repeatability check

1. Stop local Dagit session:
   - `bash tools/quality/local-stack/stop-dagit-local.sh`
2. Start it again using the same command sequence.
3. Confirm startup and visibility checks still pass.

## Troubleshooting

1. Symptom: Startup command fails immediately.
   - Likely cause: missing prerequisite or incorrect working directory.
   - Recovery: complete missing setup and rerun from repository root.
2. Symptom: Endpoint does not load in browser.
   - Likely cause: runtime did not start correctly or local endpoint conflict.
   - Recovery: stop conflicting process, restart Dagit, retest endpoint.
3. Symptom: UI loads but definitions are empty.
   - Likely cause: workspace loading issue or incomplete local environment.
   - Recovery: verify definitions entrypoint configuration and required services, then restart.

Failure categories emitted by helpers:

- `prerequisite_missing`
- `endpoint_unavailable`
- `workspace_load_failed`
- `partial_environment`

## Troubleshooting Validation Walkthrough

Run this sequence to validate recovery guidance end-to-end:

1. Simulate prerequisite failure by running startup helper outside repository root and confirm `DAGIT_FAILURE_CATEGORY=prerequisite_missing`.
2. Simulate endpoint failure with an invalid endpoint override and confirm `DAGIT_FAILURE_CATEGORY=endpoint_unavailable`:
   - `DAGIT_ENDPOINT=http://127.0.0.1:9 DAGIT_ENDPOINT_RETRIES=1 bash tools/quality/local-stack/test-dagit-endpoint.sh`
3. Simulate workspace-load failure by forcing workspace verification against an endpoint returning no location entries.
4. Confirm each failure includes a remediation hint and rerun normal startup/endpoint flow until `DAGIT_HEALTH_STATUS=ready`.

## Quality Gate Commands

1. Pipeline checks:
   - uv run --project apps/pipeline ruff check apps/pipeline
   - uv run --project apps/pipeline ty check apps/pipeline
   - uv run --project apps/pipeline pytest apps/pipeline/tests
2. Local-stack checks:
   - bash tools/quality/local-stack/test-db-readiness.sh
   - bash tools/quality/local-stack/test-compose-stack.sh

## Verified Foundational Checkpoint (2026-03-22)

Commands executed:

1. `uv run --project apps/pipeline ruff check apps/pipeline`
2. `uv run --project apps/pipeline ty check apps/pipeline`
3. `uv run --project apps/pipeline pytest apps/pipeline/tests`

Observed results:

- Ruff: `All checks passed!`
- Ty: `All checks passed!`
- Pytest: `115 passed, 1 skipped`
- Coverage: `Required test coverage of 90% reached. Total coverage: 93.49%`

## Final Verified Startup/Verification Output (2026-03-22)

Executed sequence:

1. `bash tools/quality/local-stack/start-dagit-local.sh`
2. `bash tools/quality/local-stack/test-dagit-endpoint.sh`
3. `bash tools/quality/local-stack/stop-dagit-local.sh`

Observed output:

- `DAGIT_START_STATUS=ready`
- `DAGIT_ENDPOINT=http://127.0.0.1:3001`
- `DAGIT_HEALTH_STATUS=ready`
- `DAGIT_LOCATION_ENTRIES=1`
- `DAGIT_STOP_STATUS=stopped_forced`

## Compose + Dagit Verification (2026-03-22)

Executed:

- `bash tools/quality/local-stack/start-dagit-local.sh`
- `VERIFY_DAGIT_ENDPOINT=1 bash tools/quality/local-stack/test-compose-stack.sh`
- `bash tools/quality/local-stack/stop-dagit-local.sh`

Observed result:

- Compose services started and passed baseline checks.
- Dagit endpoint/workspace probe returned `DAGIT_HEALTH_STATUS=ready`.

## Startup Benchmark (5 Runs)

Benchmark command used the startup helper across 5 stop/start cycles.

- Run 1: 0.045s
- Run 2: 0.030s
- Run 3: 0.039s
- Run 4: 0.038s
- Run 5: 0.038s
- Median: 0.038s
- P95: 0.045s

## Uninterrupted End-to-End Validation

Validation flow:

1. Start Dagit helper returns ready.
2. Endpoint/workspace helper returns ready with at least one workspace location entry.
3. Definitions catalog confirms `ingest_job` is present as a detail-view target.

Pass/Fail evidence:

- Status: PASS
- Artifacts: startup helper output, endpoint helper output, and integration test assertions in orchestration smoke/runtime tests.

## Troubleshooting Sample Protocol and Measured Resolution Rate

Sample protocol:

- Issue set: four categories (`prerequisite_missing`, `endpoint_unavailable`, `workspace_load_failed`, `partial_environment`).
- Pass criteria: category is emitted, remediation hint is present, and normal startup+endpoint flow is restored after recovery.
- Denominator: 4 simulated issue classes.

Measured result:

- Resolved categories: 4/4
- Resolution rate: 100%
