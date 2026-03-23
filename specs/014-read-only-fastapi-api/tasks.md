# Tasks: Initial Read-Only FastAPI API For Ingested Data

**Input**: Design documents from `/specs/014-read-only-fastapi-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/phase1-api-contract.md, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add FastAPI/uvicorn dependencies, create module skeleton, update Docker Compose backend service, and prepare `specs/contracts/` directory.

- [ ] T001 Add `fastapi>=0.115.0`, `uvicorn[standard]>=0.32.0`, and `httpx>=0.28.0` (test client) to apps/backend/pyproject.toml and sync lockfile with `uv add --project apps/backend fastapi "uvicorn[standard]" && uv add --project apps/backend --dev httpx`
- [ ] T002 [P] Create module skeleton: `apps/backend/src/api/__init__.py`, `apps/backend/src/api/schemas/__init__.py`, `apps/backend/src/api/routers/__init__.py`, `apps/backend/src/repositories/__init__.py`
- [ ] T003 [P] Create test skeleton directories: `apps/backend/tests/api/__init__.py`, `apps/backend/tests/repositories/__init__.py`
- [ ] T004 [P] Create `specs/contracts/` directory (parent for OpenAPI snapshot) at `specs/contracts/.gitkeep` (placeholder until snapshot is generated)
- [ ] T005 [P] Update `docker-compose.yml` backend service: replace placeholder `python -m http.server 8080` command with uvicorn FastAPI startup command mounting the workspace volume; update healthcheck to `GET /health`

- [ ] T006 Create Alembic migration `0008_query_support_indexes` with 6 query-support indexes in `libs/db/alembic/versions/0008_query_support_indexes.py`: `ix_conflict_records_run_id`, `ix_conflict_records_source_key`, `ix_conflict_records_series_key`, `ix_conflict_records_reference_period_key`, `ix_conflict_records_conflict_state` (all on `conflict_records`), and `ix_ingestion_runs_started_at` (on `ingestion_runs` for `ORDER BY started_at DESC`)

**Checkpoint**: Setup complete — dependencies installed, skeleton dirs created, compose updated

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure shared by all user stories — app factory, DB session dependency, error handlers, common Pydantic schemas, and base repository layer. MUST be complete before any user story phase begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T007 Create FastAPI application factory in `apps/backend/src/api/app.py`: `create_app()` function that registers routers, registers exception handlers for `HTTPException` and `RequestValidationError`, and configures structlog logging
- [ ] T008 [P] Implement per-request DB session dependency in `apps/backend/src/api/dependencies.py`: `get_db_session()` yield dependency using `libs/db` `resolve_database_url()`, `create_db_engine()`, and `session_scope()` utilities
- [ ] T009 [P] Implement common Pydantic response schemas in `apps/backend/src/api/schemas/common.py`: `PaginatedResponse[T]` generic envelope (`items`, `total`, `page`, `page_size`) and `ErrorResponse` envelope (`code`, `message`, `details`, `correlation_id`)
- [ ] T010 [P] Register centralized exception handlers in `apps/backend/src/api/app.py`: override FastAPI default `HTTPException` handler and `RequestValidationError` handler to return `ErrorResponse` envelope with stable `code`/`message`/`details` fields
- [ ] T011 [P] Create `apps/backend/src/repositories/base.py` with shared pagination helper (`apply_pagination(query, page, page_size) -> tuple[list, int]`) used by all read repositories
- [ ] T012 [P] Add foundational tests for app factory, dependency injection, and error handler envelope shape in `apps/backend/tests/api/test_app_foundation.py`
- [ ] T013 [P] Add foundational tests for `PaginatedResponse` and `ErrorResponse` schema validation in `apps/backend/tests/api/test_schemas_common.py`
- [ ] T014 Add main ASGI entrypoint `apps/backend/src/api/main.py` exporting `app = create_app()` so uvicorn can start with `src.api.main:app`

**Checkpoint**: Foundation ready — app factory, DB session DI, error handlers, common schemas, and pagination helper all complete. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 — Check API Health (Priority: P1) 🎯 MVP

**Goal**: A frontend client or operator can confirm the backend API is reachable and verify database connectivity via `GET /health`.

**Independent Test**: `curl http://localhost:8080/health` returns HTTP 200 `{"status": "ok", "db": "reachable"}` when the database is up; returns HTTP 503 `{"status": "unavailable", "db": "unreachable"}` when the database is not reachable.

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T015 [P] [US1] Add health endpoint tests in `apps/backend/tests/api/test_health.py`: test 200 response shape when DB is reachable (mock session), test 503 response shape and error envelope when DB raises connection error

### Implementation for User Story 1

- [ ] T016 [US1] Implement `HealthResponse` Pydantic schema in `apps/backend/src/api/schemas/common.py` (add to existing file): fields `status: str` and `db: str`
- [ ] T017 [US1] Implement `GET /health` router in `apps/backend/src/api/routers/health.py`: execute a lightweight DB probe (e.g., `SELECT 1`), return `HealthResponse(status="ok", db="reachable")` on success, return HTTP 503 `ErrorResponse` with `code="service_unavailable"` on DB error; do not use the standard DI session — probe directly to isolate health from request session lifecycle
- [ ] T018 [US1] Register health router on the FastAPI app in `apps/backend/src/api/app.py` (prefix-free: `/health`)
- [ ] T019 [US1] Verify US1 coverage contribution keeps backend >= 90% by running `uv run --project apps/backend pytest apps/backend/tests` and reviewing coverage report

**Checkpoint**: User Story 1 independently testable — health endpoint responds correctly under healthy and degraded database conditions

---

## Phase 4: User Story 2 — List Ingestion Runs (Priority: P1)

**Goal**: A frontend operator can retrieve all ingestion runs ordered by descending start time, with pagination, via `GET /api/runs`.

**Independent Test**: Seed the database with ingestion run records, send `GET /api/runs`, verify HTTP 200 with a paginated list ordered by `started_at` descending; send `GET /api/runs` with no records, verify HTTP 200 with `items: []` and `total: 0`.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T020 [P] [US2] Add run list endpoint tests in `apps/backend/tests/api/test_runs.py`: test paginated list shape, descending order, empty list case, and pagination parameters (page/page_size validation with 422 on invalid values)
- [ ] T021 [P] [US2] Add run repository unit tests in `apps/backend/tests/repositories/test_run_repository.py`: test `list_runs(page, page_size)` returns ordered results and correct total count using in-memory SQLite or mock session

### Implementation for User Story 2

- [ ] T022 [P] [US2] Implement `IngestionRunResponse` Pydantic schema in `apps/backend/src/api/schemas/runs.py`: all fields from `IngestionRun` ORM model with `model_config = ConfigDict(from_attributes=True)` and `datetime` → ISO-8601 UTC string serialization
- [ ] T023 [US2] Implement `RunRepository` in `apps/backend/src/repositories/run_repository.py`: `list_runs(session, page, page_size) -> tuple[list[IngestionRun], int]` ordered by `started_at` DESC using `libs/db` `IngestionRun` ORM model
- [ ] T024 [US2] Implement `GET /api/runs` router in `apps/backend/src/api/routers/runs.py`: inject DB session, call `RunRepository.list_runs()`, return `PaginatedResponse[IngestionRunResponse]`; validate `page >= 1` and `1 <= page_size <= 200` returning 422 on violations
- [ ] T025 [US2] Register runs router on the FastAPI app in `apps/backend/src/api/app.py` (prefix `/api`)
- [ ] T026 [US2] Verify US2 coverage keeps backend >= 90% by running `uv run --project apps/backend pytest apps/backend/tests`

**Checkpoint**: User Story 2 independently testable — paginated run list endpoint works with and without seeded data

---

## Phase 5: User Story 3 — Retrieve a Single Ingestion Run (Priority: P2)

**Goal**: A developer can retrieve the full detail record for a specific run by its string identifier via `GET /api/runs/{run_id}`.

**Independent Test**: Seed a known run, issue `GET /api/runs/{run_id}`, verify HTTP 200 with the expected full detail object; issue `GET /api/runs/nonexistent`, verify HTTP 404 with `{"code": "not_found", ...}` envelope.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T027 [P] [US3] Add single-run detail tests in `apps/backend/tests/api/test_runs.py` (extend existing file): test 200 detail shape with seeded run, test 404 envelope for unknown run_id

### Implementation for User Story 3

- [ ] T028 [US3] Add `get_run_by_run_id(session, run_id: str) -> IngestionRun | None` method to `RunRepository` in `apps/backend/src/repositories/run_repository.py`
- [ ] T029 [US3] Add `GET /api/runs/{run_id}` route to `apps/backend/src/api/routers/runs.py`: call `RunRepository.get_run_by_run_id()`, return `IngestionRunResponse` on success, raise `HTTPException(404)` with `ErrorResponse` body when `None`
- [ ] T030 [US3] Verify US3 coverage keeps backend >= 90% by running `uv run --project apps/backend pytest apps/backend/tests`

**Checkpoint**: User Story 3 independently testable — single-run detail and 404 both work

---

## Phase 6: User Story 4 — List Source Run Outcomes For a Run (Priority: P2)

**Goal**: A frontend client can retrieve all per-source outcome records for a specific ingestion run via `GET /api/runs/{run_id}/outcomes`.

**Independent Test**: Seed a run with associated source outcomes, send `GET /api/runs/{run_id}/outcomes`, verify HTTP 200 with all outcomes and correct `state` values; send `GET /api/runs/nonexistent/outcomes`, verify HTTP 404.

### Tests for User Story 4 (REQUIRED) ⚠️

- [ ] T031 [P] [US4] Add outcomes endpoint tests in `apps/backend/tests/api/test_outcomes.py`: test list with seeded outcomes, empty list for run with no outcomes, 404 for unknown run_id, stable `state` values from enum set
- [ ] T032 [P] [US4] Add outcome repository unit tests in `apps/backend/tests/repositories/test_outcome_repository.py`: test `list_outcomes_for_run(session, run_id)` returns all matching rows

### Implementation for User Story 4

- [ ] T033 [P] [US4] Implement `SourceRunOutcomeResponse` Pydantic schema in `apps/backend/src/api/schemas/outcomes.py` with `from_attributes=True` and UTC timestamp serialization
- [ ] T034 [US4] Implement `OutcomeRepository` in `apps/backend/src/repositories/outcome_repository.py`: `list_outcomes_for_run(session, run_id: str, page, page_size) -> tuple[list[SourceRunOutcome], int]` using `libs/db` `SourceRunOutcome` ORM model
- [ ] T035 [US4] Implement `GET /api/runs/{run_id}/outcomes` router in `apps/backend/src/api/routers/outcomes.py`: verify run exists (reuse `RunRepository.get_run_by_run_id()`, raise 404 if not found), call `OutcomeRepository.list_outcomes_for_run()`, return `PaginatedResponse[SourceRunOutcomeResponse]`
- [ ] T036 [US4] Register outcomes router on the FastAPI app in `apps/backend/src/api/app.py` (prefix `/api`)
- [ ] T037 [US4] Verify US4 coverage keeps backend >= 90% by running `uv run --project apps/backend pytest apps/backend/tests`

**Checkpoint**: User Story 4 independently testable — outcomes list and 404 both work per run

---

## Phase 7: User Story 5 — List Eligibility Records For a Run (Priority: P3)

**Goal**: A developer or operator can inspect source eligibility evaluations for a specific run via `GET /api/runs/{run_id}/eligibility`.

**Independent Test**: Seed a run with eligibility records, send `GET /api/runs/{run_id}/eligibility`, verify HTTP 200 with `source_key`, `eligibility_state` (one of `due`, `not_due`, `skipped_inactive`, `skipped_invalid_policy`), and `reason_code` fields; send with unknown `run_id`, verify HTTP 404.

### Tests for User Story 5 (REQUIRED) ⚠️

- [ ] T038 [P] [US5] Add eligibility endpoint tests in `apps/backend/tests/api/test_eligibility.py`: test list with seeded eligibility records, empty list case, 404 for unknown run_id, correct field names
- [ ] T039 [P] [US5] Add eligibility repository unit tests in `apps/backend/tests/repositories/test_eligibility_repository.py`: test `list_eligibility_for_run(session, run_id)` returns all matching rows

### Implementation for User Story 5

- [ ] T040 [P] [US5] Implement `SourceEligibilityResponse` Pydantic schema in `apps/backend/src/api/schemas/eligibility.py` with `from_attributes=True` and UTC timestamp serialization
- [ ] T041 [US5] Implement `EligibilityRepository` in `apps/backend/src/repositories/eligibility_repository.py`: `list_eligibility_for_run(session, run_id: str, page, page_size) -> tuple[list[SourceEligibilitySnapshot], int]` using `libs/db` `SourceEligibilitySnapshot` ORM model
- [ ] T042 [US5] Implement `GET /api/runs/{run_id}/eligibility` router in `apps/backend/src/api/routers/eligibility.py`: verify run exists (raise 404 if not), call `EligibilityRepository.list_eligibility_for_run()`, return `PaginatedResponse[SourceEligibilityResponse]`
- [ ] T043 [US5] Register eligibility router on the FastAPI app in `apps/backend/src/api/app.py` (prefix `/api`)
- [ ] T044 [US5] Verify US5 coverage keeps backend >= 90% by running `uv run --project apps/backend pytest apps/backend/tests`

**Checkpoint**: User Story 5 independently testable — eligibility list and 404 both work per run

---

## Phase 8: User Story 6 — List Conflicts With Filters (Priority: P3)

**Goal**: A data quality reviewer can browse conflict records across ingestion runs with optional filter parameters via `GET /api/conflicts`.

**Independent Test**: Seed conflicts with varying attributes, issue `GET /api/conflicts` with each supported filter parameter (`run_id`, `source_key`, `series_key`, `reference_period_key`, `conflict_state`), verify only matching records are returned; issue with unsupported parameter, verify HTTP 422.

### Tests for User Story 6 (REQUIRED) ⚠️

- [ ] T045 [P] [US6] Add conflicts endpoint tests in `apps/backend/tests/api/test_conflicts.py`: test unfiltered paginated list, each filter parameter independently, empty result for non-matching filter, 422 for invalid `conflict_state` value, 422 for out-of-range pagination params
- [ ] T046 [P] [US6] Add conflict repository unit tests in `apps/backend/tests/repositories/test_conflict_repository.py`: test `list_conflicts()` with each filter combination returns correct subset

### Implementation for User Story 6

- [ ] T047 [P] [US6] Implement `ConflictRecordResponse` Pydantic schema in `apps/backend/src/api/schemas/conflicts.py` with `from_attributes=True` and UTC timestamp serialization
- [ ] T048 [US6] Implement `ConflictRepository` in `apps/backend/src/repositories/conflict_repository.py`: `list_conflicts(session, *, run_id, source_key, series_key, reference_period_key, conflict_state, page, page_size) -> tuple[list[ConflictRecord], int]` using `libs/db` `ConflictRecord` ORM model; apply only non-None filters; validate `conflict_state` against the stable value set (`open`, `resolved`, `suppressed`)
- [ ] T049 [US6] Implement `GET /api/conflicts` router in `apps/backend/src/api/routers/conflicts.py`: accept all five optional filter query params, validate `conflict_state` enum (return 422 `ErrorResponse` with `details` on invalid value), call `ConflictRepository.list_conflicts()`, return `PaginatedResponse[ConflictRecordResponse]`
- [ ] T050 [US6] Register conflicts router on the FastAPI app in `apps/backend/src/api/app.py` (prefix `/api`)
- [ ] T051 [US6] Verify US6 coverage keeps backend >= 90% by running `uv run --project apps/backend pytest apps/backend/tests`

**Checkpoint**: All six user stories independently functional and testable

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: OpenAPI snapshot, Docker Compose validation, documentation updates, and final quality gate pass.

- [ ] T052 [P] Generate OpenAPI contract snapshot from the running app and save to `specs/contracts/openapi-phase1-snapshot.json`: run `uv run --project apps/backend python -c "import json; from src.api.app import create_app; print(json.dumps(create_app().openapi(), indent=2))" > specs/contracts/openapi-phase1-snapshot.json`
- [ ] T053 [P] Add OpenAPI snapshot consistency test in `apps/backend/tests/api/test_openapi_snapshot.py`: use `TestClient` to fetch `/openapi.json` and compare against the checked-in snapshot, failing if they diverge (satisfies FR-015 / SC-004)
- [ ] T054 [P] Create backend API local run runbook in `docs/runbooks/backend-api-local-run.md`: document `uv sync`, uvicorn start command, health check curl, Swagger UI URL, and Docker Compose start sequence per quickstart.md
- [ ] T055 [P] Update `AGENTS.md` to reflect new backend API structure (`apps/backend/src/api/`, `apps/backend/src/repositories/`), new dependencies (FastAPI, uvicorn, httpx), and the uvicorn start command
- [ ] T056 Run full backend quality gate suite and confirm all pass: `uv run --project apps/backend ruff check apps/backend && uv run --project apps/backend ruff format --check apps/backend && uv run --project apps/backend ty check apps/backend && uv run --project apps/backend pytest apps/backend/tests`
- [ ] T057 [P] Run affected Nx quality targets: `pnpm run affected:lint && pnpm run affected:format && pnpm run affected:typecheck && pnpm run affected:test && pnpm run affected:coverage`
- [ ] T058 Start Docker Compose local stack and validate backend service health: `docker compose up -d && docker compose ps` — confirm backend service reports healthy and `curl http://localhost:8080/health` returns `{"status": "ok", "db": "reachable"}`
- [ ] T059 Perform final consistency pass — confirm plan.md, spec.md, data-model.md, contracts/phase1-api-contract.md, and OpenAPI snapshot are all mutually consistent in `specs/014-read-only-fastapi-api/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 completion — MVP, can start independently
- **US2 (Phase 4)**: Depends on Phase 2 completion — can run in parallel with US1
- **US3 (Phase 5)**: Depends on Phase 4 (reuses `RunRepository`)
- **US4 (Phase 6)**: Depends on Phase 4 (reuses `RunRepository.get_run_by_run_id()`)
- **US5 (Phase 7)**: Depends on Phase 4 (reuses `RunRepository.get_run_by_run_id()`)
- **US6 (Phase 8)**: Depends on Phase 2 only — fully independent of other story phases
- **Polish (Phase 9)**: Depends on all user story phases complete

### User Story Dependencies

- **US1 (P1)**: Independent after Foundational — health probe needs only `dependencies.py`
- **US2 (P1)**: Independent after Foundational — builds `RunRepository`
- **US3 (P2)**: Depends on US2 (`RunRepository` must exist)
- **US4 (P2)**: Depends on US2 (`RunRepository.get_run_by_run_id()` needed for 404 guard)
- **US5 (P3)**: Depends on US2 (`RunRepository.get_run_by_run_id()` needed for 404 guard)
- **US6 (P3)**: Independent after Foundational — uses only `ConflictRepository`

### Within Each User Story

- Tests first (confirm failing baseline before implementation)
- Schema (Pydantic) and repository before router
- Router before registering on app factory
- Coverage verification before marking phase complete

### Parallel Opportunities

- All Phase 1 [P] tasks run in parallel
- All Phase 2 [P] tasks run in parallel after T007 starts
- US1 and US2 can run in parallel after Phase 2 completes
- US3, US4, US5, US6 can each start as soon as their dependency story is complete
- Within each story, test tasks [P] and schema tasks [P] can run in parallel
- Polish tasks T052–T055 and T057 can run in parallel after all stories complete

---

## Parallel Example: User Story 2

```bash
# Launch US2 tests and schema in parallel:
Task: "T020 [US2] Add run list endpoint tests in apps/backend/tests/api/test_runs.py"
Task: "T021 [US2] Add run repository unit tests in apps/backend/tests/repositories/test_run_repository.py"
Task: "T022 [US2] Implement IngestionRunResponse schema in apps/backend/src/api/schemas/runs.py"

# Then implement sequentially:
Task: "T023 [US2] Implement RunRepository in apps/backend/src/repositories/run_repository.py"
Task: "T024 [US2] Implement GET /api/runs router in apps/backend/src/api/routers/runs.py"
Task: "T025 [US2] Register runs router in apps/backend/src/api/app.py"
```

## Parallel Example: Polish Phase

```bash
# All documentation and snapshot tasks in parallel:
Task: "T052 Generate OpenAPI snapshot to specs/contracts/openapi-phase1-snapshot.json"
Task: "T053 Add OpenAPI snapshot consistency test in apps/backend/tests/api/test_openapi_snapshot.py"
Task: "T054 Create backend API runbook in docs/runbooks/backend-api-local-run.md"
Task: "T055 Update AGENTS.md with backend API structure and commands"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (health endpoint)
4. Complete Phase 4: User Story 2 (run list endpoint)
5. **STOP and VALIDATE**: Run `uv run --project apps/backend pytest apps/backend/tests` and `curl http://localhost:8080/api/runs`
6. Confirm MVP is independently deployable

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 + US2 → MVP (health + run list) → Validate → Demo
3. US3 + US4 → Single run + outcomes drill-down → Validate
4. US5 + US6 → Eligibility + conflicts → Validate
5. Polish → OpenAPI snapshot, docs, AGENTS.md → Full quality gate pass

### Parallel Team Strategy

With two developers after Phase 2 completes:

- Developer A: US1 (health), then US3 (single run detail), then US5 (eligibility)
- Developer B: US2 (run list) — provides `RunRepository` — then US4 (outcomes), then US6 (conflicts)
- Merge and polish together in Phase 9

---

## Notes

- [P] tasks = different files, no dependencies on tasks still in progress
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Coverage MUST remain >= 90% in every affected project after every phase
- Relevant documentation MUST be updated in the same change as impacted code
- AGENTS.md MUST be updated when repository structure, workflows, or canonical commands change
- Verify tests fail before implementing (TDD baseline)
- Commit after each task or logical group
- Stop at each Checkpoint to validate story independently before proceeding
- Avoid: vague tasks, same-file conflicts between parallel tasks, cross-story dependencies that break independence
