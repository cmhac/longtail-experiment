---
name: manual-testing
description: "Run agentic manual testing in the real local dev environment before final quality gates. Use when implementing or fixing code to execute real commands, exercise real runtime paths with realistic data, inspect logs and database state, and iterate fix-and-retest until behavior is correct."
compatibility: Requires local stack tooling (docker compose, uv, pnpm, browser automation tools)
metadata:
  author: longtail-experiment
  source: local manual testing standard
---

# Manual Testing Skill

## User Input

```text
$ARGUMENTS
```

You MUST consider the user input before proceeding (if not empty).

## Purpose

Do not rely on tests and lint/type checks alone. Always execute real runtime behavior in the local development environment and validate that the feature works end to end.

## Core Rules

1. Never assume generated code works until it has been executed.
2. Run automated tests and quality checks, then run manual runtime checks.
3. Use realistic inputs and real runtime surfaces whenever possible.
4. If manual testing reveals a defect, fix it and repeat the manual loop.
5. Add or update automated tests for defects found during manual testing.
6. Record what you ran and what you observed.
7. For browser-driven UI flows, use the `use-chrome-browser` skill for Rodney-based interactions.

## Required Manual Testing Loop

1. Identify impacted area(s) from changed files and task scope.
2. Start from a clean runtime state before manual checks:
   - `docker compose down`
   - `docker compose up -d`
   - `docker compose ps`
3. Execute area-specific manual checks (choose all that apply).
4. Verify expected outputs from runtime behavior, logs, and data state.
5. If anything fails or looks wrong:
   - fix code,
   - rerun relevant automated tests,
   - rerun manual checks from clean state.
6. Continue until manual checks and quality gates both pass.

## Area-Specific Manual Checks

### A) Changes under `libs/`

1. Exercise the changed library code directly using realistic inputs.
2. Prefer quick execution with `python -c` for targeted checks.
3. For larger flows, create a temporary script outside tracked files (for example under `/tmp`) and run it.
4. Include edge cases and failure paths relevant to the change.
5. Confirm returned values and side effects match expectations.

### B) Changes under `apps/pipeline/`

1. Restart local stack from clean state.
2. Bring up required services with Docker Compose (including Dagster surfaces used in this repo).
3. Run real pipeline materialization/ingest flow for the modified behavior.
4. Inspect Dagster logs and runtime service logs:
   - `docker compose logs dagit`
   - `docker compose logs backend`
   - use service-specific logs as needed.
5. Verify persistence in PostgreSQL by querying expected records with `docker compose exec db psql ...`.
6. Confirm created/updated records match expected values and lineage.

### C) Changes under `apps/backend/`

1. Restart from clean local stack.
2. Start backend runtime through Docker Compose.
3. Populate data through the real pipeline path (run the relevant ingestion/materialization flow first).
4. Run real API requests (for example with `curl`) against local backend endpoints.
5. Validate response payload structure and values against expected behavior.
6. Verify DB state supports returned API data where applicable.

### D) Changes under `apps/frontend/`

1. Prepare backend data first (pipeline + backend runtime) so UI has realistic data.
2. Run frontend in local runtime.
3. Use browser automation tools to open impacted pages and exercise user flows.
4. Prefer the `use-chrome-browser` skill when using Rodney for browser automation.
   - Follow that skill's mandatory first step: run `uvx rodney --help` before any other Rodney command.
   - Use Rodney lifecycle commands (`start`/`stop`) to keep sessions explicit and clean.
5. Check browser console for runtime errors.
6. Capture screenshots of impacted views and verify visual/interaction correctness.
7. Validate loading, empty, and error states relevant to the change.

## Cross-Area Checks

If changes span multiple areas (for example pipeline + backend, or backend + frontend), execute all applicable loops end to end in dependency order.

Suggested dependency order:

1. `libs` / shared logic
2. `apps/pipeline`
3. `apps/backend`
4. `apps/frontend`

## Evidence Required In Final Report

Always include a concise manual testing record:

1. Commands executed.
2. Runtime surfaces exercised (services/endpoints/pages).
3. Key observed outputs (logs, API responses, DB query results).
4. Screenshot references for UI work.
5. Defects found and how they were fixed.
6. Confirmation that manual loop was completed before final quality gate completion.

## Completion Condition

The task is not complete until:

1. Required manual runtime checks have passed for all impacted areas.
2. Any defects found were fixed and revalidated.
3. Automated quality gates also pass.
