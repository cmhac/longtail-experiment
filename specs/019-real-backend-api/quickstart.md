# Quickstart: Real Backend Discovery API Runtime

## Objective

Validate that discovery API runtime behavior is fully persisted-data-backed, fixtures are test-only, and ingest-to-API parity is demonstrable in the local stack.

## Prerequisites

- Repository dependencies installed.
- Backend and pipeline Python environments synced.
- Local stack secrets configured for real ingest when required.
- Feature branch `019-real-backend-api` checked out.

## 1) Start local stack and confirm readiness

```bash
docker compose up -d
bash tools/quality/local-stack/test-db-readiness.sh
bash tools/quality/local-stack/run-db-migrations.sh
bash tools/quality/local-stack/check-db-revision.sh
```

Expected:

- Containers are healthy.
- Database is reachable.
- Migration head matches repository expectations.

## 2) Capture baseline API responses

```bash
curl -sS http://localhost:8000/api/datasets/recent
curl -sS http://localhost:8000/api/datasets/INT.US.FEDFUNDS
```

Expected:

- Responses are successful and stable for repeated identical requests.
- Baseline payloads are saved for parity comparison.

## 3) Execute ingest update against persisted store

Run the documented ingest command path used by local verification (with required environment variables and source selection).

Expected:

- Ingest command reports persisted write outcomes.
- At least one dataset recency or observation payload is updated.

## 4) Re-check discovery endpoints for parity

```bash
curl -sS http://localhost:8000/api/datasets/recent
curl -sS http://localhost:8000/api/datasets/INT.US.FEDFUNDS
```

Expected:

- At least one response changes to reflect newly persisted records.
- Detail observations remain chronological.
- Unknown dataset requests still return explicit not-found behavior.

## 5) Verify fixture prohibition in runtime and run tests

Run affected backend quality and tests, including integration coverage for ingest-to-API parity and runtime fixture prohibition checks.

Suggested commands:

```bash
uv run --project apps/backend ruff check apps/backend
uv run --project apps/backend ruff format --check apps/backend
uv run --project apps/backend ty check apps/backend
uv run --project apps/backend pytest apps/backend/tests
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Expected:

- Quality gates pass without suppressions.
- Tests confirm fixture-backed behavior is allowed only in tests and not reachable by runtime startup.
- Ingest-to-API parity assertion passes.

## Acceptance Evidence Checklist

- Runtime responses are sourced from persisted records.
- Runtime startup path does not use fixture-backed discovery wiring.
- Fixtures are used only in automated tests.
- Ingest-to-API parity is proven by observed response delta.
- Deterministic ordering and not-found semantics remain intact.
