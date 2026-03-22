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

1. Run the documented local startup command for Dagit.
2. Wait for readiness output indicating the UI endpoint is available.
3. If startup fails, capture the failure category and proceed to troubleshooting.

## Step 3: Open UI and verify workspace load

1. Open the local Dagit endpoint in a browser.
2. Confirm the landing page loads without blocking errors.
3. Confirm existing repository definitions appear in at least one listing view.

## Step 4: Verify definition details

1. Open one visible definition from the listing page.
2. Confirm detail view loads and displays expected metadata.
3. Record verification outcome as pass/fail.

## Step 5: Repeatability check

1. Stop local Dagit session.
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

## Quality Gate Commands

1. Pipeline checks:
   - uv run --project apps/pipeline ruff check apps/pipeline
   - uv run --project apps/pipeline ty check apps/pipeline
   - uv run --project apps/pipeline pytest apps/pipeline/tests
2. Local-stack checks:
   - bash tools/quality/local-stack/test-db-readiness.sh
   - bash tools/quality/local-stack/test-compose-stack.sh
