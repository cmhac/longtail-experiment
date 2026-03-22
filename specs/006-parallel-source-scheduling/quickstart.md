# Quickstart: Parallel Source Scheduling and Bounded Concurrency

## Goal

Verify that orchestration runs sources with bounded parallelism and source-specific cadence eligibility while preserving run audit visibility.

## Prerequisites

- Git
- Docker or Docker Desktop
- Node.js 22 LTS
- pnpm
- Python 3.12
- uv

## 1. Bootstrap Workspace

```bash
pnpm install
uv sync --project apps/pipeline --frozen
uv sync --project apps/backend --frozen
```

## 2. Prepare Local Database

```bash
docker compose up -d db
bash tools/quality/local-stack/run-db-migrations.sh
bash tools/quality/local-stack/check-db-revision.sh
```

Expected outcome:

- Database is healthy and current migration revision is applied.

## 3. Run Core Orchestration Tests

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration
```

Expected outcome:

- Baseline orchestration contracts pass before cadence/parallelism assertions.

## 4. Verify Per-Source Cadence Selection

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration -k "cadence or due or schedule_policy"
```

Expected outcome:

- Only due sources are selected for scheduled runs.
- Not-due sources are recorded with explicit non-execution reasons.

## 5. Verify Bounded Parallelism

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration -k "parallel or concurrency or queue"
```

Expected outcome:

- Active source executions never exceed configured max parallelism.
- Due sources beyond capacity wait and are launched as slots become available.

## 6. Verify On-Demand Subset Runs

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration -k "on_demand and subset"
```

Expected outcome:

- Operator-requested source subsets execute without mutating cadence policy state.

## 7. Verify Persisted Run Visibility

```bash
cd apps/pipeline
uv run python -c "from src.orchestration.definitions import defs, get_ingest_runtime; runtime = get_ingest_runtime(); result = defs.get_job_def('ingest_job').execute_in_process(tags={'trigger_type': 'scheduled', 'requested_by': 'quickstart'}); payload = result.output_for_node('execute_ingest_run'); print(payload)"
```

Expected outcome:

- Run summary includes due/executed/deferred/not-due source counts.
- Persisted runtime records contain source-level eligibility and terminal outcomes.

## 8. Run Quality Gates

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
pnpm run affected:duplication
```

## 9. Documentation Impact Checklist

Update in same change when behavior or commands change:

- AGENTS.md
- docs/architecture/monorepo-boundaries.md
- docs/onboarding/monorepo-baseline.md
- docs/runbooks/local-stack-baseline.md
