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
docker compose ps
docker compose up -d backend
docker compose exec db psql -U "${LOCAL_DB_USER:-longtail}" -d "${LOCAL_DB_NAME:-longtail_local}" -c "SELECT version_num FROM alembic_version;"
```

Migration-head runtime enforcement reference:

```bash
DISCOVERY_EXPECTED_DB_REVISION=0010_source_profile_metadata
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
bash tools/quality/local-stack/test-discovery-persisted-parity.sh
```

Optional parity command with ingest delta check:

```bash
DISCOVERY_PARITY_REQUIRE_DELTA=1 \
DISCOVERY_PARITY_INGEST_COMMAND="<run-ingest-command>" \
bash tools/quality/local-stack/test-discovery-persisted-parity.sh
```

Expected:

- Quality gates pass without suppressions.
- Tests confirm fixture-backed behavior is allowed only in tests and not reachable by runtime startup.
- Ingest-to-API parity assertion passes.
- Parity script confirms runtime endpoints are persisted-data-backed and not fixture-backed.

## Acceptance Evidence Checklist

- Runtime responses are sourced from persisted records.
- Runtime startup path does not use fixture-backed discovery wiring.
- Fixtures are used only in automated tests.
- Ingest-to-API parity is proven by observed response delta.
- Deterministic ordering and not-found semantics remain intact.

## Execution Evidence (2026-03-23)

### Backend quality suite

```bash
uv run --project apps/backend ruff check apps/backend
uv run --project apps/backend ruff format --check apps/backend
uv run --project apps/backend ty check apps/backend
uv run --project apps/backend pytest apps/backend/tests
```

Observed outcome:

- Lint/format/typecheck passed.
- Backend tests passed: `82 passed`.
- Backend coverage threshold passed: `96.68%` total (`>= 90%`).

### Affected workspace quality gates

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Observed outcome:

- All affected gates passed for `frontend`, `pipeline`, and `backend`.

### Local stack parity flow

```bash
docker compose up -d
docker compose exec db psql -U "${LOCAL_DB_USER:-longtail}" -d "${LOCAL_DB_NAME:-longtail_local}" -c "SELECT version_num FROM alembic_version;"
DISCOVERY_API_BASE_URL=http://127.0.0.1:8080 DISCOVERY_PARITY_REQUIRE_DELTA=0 \
	bash tools/quality/local-stack/test-discovery-persisted-parity.sh
```

Observed outcome:

- Migration head check passed: `Revision OK: 0010_source_profile_metadata`.
- Parity script passed and auto-selected a persisted dataset id from `/api/datasets/recent`.

### Manual endpoint verification against Postgres

Runtime endpoints verified from `apps/backend/src/http_api_server.py`:

- `GET /api/health`
- `GET /api/datasets/search`
- `GET /api/datasets/recent`
- `GET /api/datasets`
- `GET /api/datasets/{dataset_id}`

Manual API-vs-DB comparisons performed against local stack (`backend:8080`, `db:55432`):

- `health`: API returned `{"status":"ok"}`.
- `search`: `q=monetary` API dataset ids and recency order matched SQL result set.
- `recent`: `limit=3` API dataset ids and latest timestamps matched SQL ordering.
- `catalog`: `source_id=fred` API dataset ids and sort order matched SQL.
- `catalog grouped`: `group_by_source=true` API group counts matched SQL grouped counts.
- `detail`: metadata, topic tags, and observation chronology/value/reported_at matched SQL for `INT.US.FEDFUNDS.TEST.99f56208-aceb-4802-935c-e5e6204fa3e8`.
- `detail unknown`: API returned HTTP `404` with `dataset_not_found` code as expected.

Issues found and fixed during manual verification:

- Fixed ambiguous NULL date-parameter SQL in persisted observation query (detail endpoint crash).
- Fixed duplicate topic tag aggregation in persisted repository by using `ARRAY_AGG(DISTINCT ...)`.
- Fixed local revision-check script default head from `0007_dataset_metadata_topic_tags` to `0010_source_profile_metadata`.
