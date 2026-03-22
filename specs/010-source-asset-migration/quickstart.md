# Quickstart: Source-Per-Asset Migration

**Feature**: 010-source-asset-migration  
**Goal**: Validate the one-time cutover from coordinator-driven ingestion to source-per-asset orchestration with Dagster-only scheduling.

## Prerequisites

1. Repository dependencies are synced for pipeline and backend projects.
2. Local Docker Compose stack is available and healthy.
3. Developer runs commands from repository root.

## Step 1: Verify baseline quality before migration changes

1. Run pipeline quality checks:
   - uv run --project apps/pipeline ruff check apps/pipeline
   - uv run --project apps/pipeline ty check apps/pipeline
   - uv run --project apps/pipeline pytest apps/pipeline/tests
2. Confirm no quality gate failures before continuing.

## Step 2: Validate source registration and definition loading

1. Run orchestration smoke checks:
   - uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_definitions_smoke.py
2. Confirm all supported and newly onboarded implementation-window sources register as source assets.
3. Confirm no duplicate source key registrations are accepted.

## Step 3: Execute cutover validation path

1. Start local stack and Dagit:
   - docker compose up -d
   - bash tools/quality/local-stack/start-dagit-local.sh
2. Verify Dagit endpoint and workspace visibility:
   - DAGIT_VERIFY_WORKSPACE=1 DAGIT_MIN_LOCATION_ENTRIES=1 bash tools/quality/local-stack/test-dagit-endpoint.sh
3. Confirm source-level materializations and run outcomes are visible in Dagit.

## Step 4: Validate Dagster-only scheduling authority

1. Run orchestration cadence checks:
   - pnpm exec nx run pipeline:test:orchestration:cadence
2. Confirm no legacy non-Dagster scheduling entrypoint can initiate ingest cadence.
3. Confirm scheduled runs execute through source assets only.

## Step 5: Validate failure handling in greenfield cutover posture

1. Simulate one or more source failures in cutover window test scenarios.
2. Confirm scheduling authority remains Dagster-only.
3. Confirm failed sources remain visible for operator triage and can be recovered without re-enabling legacy scheduler paths.

## Step 6: Final local stack validation and shutdown

1. Run compose verification:
   - VERIFY_DAGIT_ENDPOINT=1 bash tools/quality/local-stack/test-compose-stack.sh
2. Stop Dagit and stack:
   - bash tools/quality/local-stack/stop-dagit-local.sh
   - docker compose down

## Documentation Verification

1. Update and review source onboarding and scheduling guidance in docs/runbooks/local-stack-baseline.md.
2. Ensure any workflow/command deltas remain aligned with AGENTS.md canonical commands.

## Acceptance Checklist

1. All sources in scope materialize as source assets.
2. Dagster is the only scheduling authority after cutover.
3. Source-level outcomes are visible for successful and failed runs.
4. Quality gates remain passing with coverage expectations intact.
