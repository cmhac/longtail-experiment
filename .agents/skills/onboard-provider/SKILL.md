---
name: onboard-provider
description:
  Implement and wire a new data source provider into the Dagster ingestion pipeline.
  Use when the user provides a description, example code, or API reference for a new
  data source to ingest. Performs feasibility assessment, builds the source adapter,
  validates it standalone, then integrates it into the pipeline.
compatibility: Requires the pipeline orchestration structure under apps/pipeline/src/orchestration/
metadata:
  author: longtail-experiment
  source: docs/runbooks/provider-onboarding.md
---

# Onboard Provider Skill

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding. The input may be:

- A verbal description of a data source and its API
- Example code or API response snippets
- A link to API documentation
- A provider name and series to add
- Any combination of the above

If the input is empty, ask the user to describe the data source they want to add.

## Mandatory Bootstrap-First Workflow

Before creating or editing adapter implementation files, you MUST:

1. Read `docs/runbooks/provider-onboarding.md`.
2. Use `pnpm run provider:bootstrap -- ...` to generate the new adapter scaffold.

Manual creation of a new adapter file is not the default path. Only proceed manually if the bootstrap command is unavailable and explicitly document the exception in your output.

---

## Phase 1: Feasibility Assessment

Before writing any code, evaluate whether the described data source fits the platform. Read these files to ground your understanding of the system constraints:

- `apps/pipeline/src/contract/schemas/canonical_observation.py` — the canonical record schema
- `apps/pipeline/src/contract/normalizers/source_payload_mapper.py` — how records are normalized
- `apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py` — reference adapter implementation
- `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py` — current registered sources and `SourceBuilderSpec`

### 1a. Extract source profile

From the user's input, identify and document:

| Property                        | Value                                                                                              |
| ------------------------------- | -------------------------------------------------------------------------------------------------- |
| **Provider name**               | The organization or platform (e.g. "BLS", "World Bank")                                            |
| **API base URL**                | The root HTTP endpoint                                                                             |
| **Authentication**              | Open, API key, OAuth, etc.                                                                         |
| **Response format**             | JSON, XML, CSV, etc.                                                                               |
| **Series to ingest**            | List each series with: provider series ID, human name, frequency, geographic scope                 |
| **Canonical series keys**       | Propose keys following the `CATEGORY.COUNTRY.SERIES` convention (e.g. `LABOR.US.UNRATE`)           |
| **Source key**                  | Propose a `source_key` following the `<provider>_<primary_series>` convention                      |
| **Provider group key**          | The provider grouping key (e.g. "bls", "worldbank")                                                |
| **Schedule cadence**            | How often new data is published (daily, weekly, monthly, quarterly)                                |
| **Backfill support**            | Whether the API accepts date-range or start-date parameters                                        |
| **Data dimensionality**         | Whether records are single-series points or a high-dimensional cube (e.g., country x class x type) |
| **Series cardinality strategy** | Static bounded series set vs dynamic/high-cardinality series generation                            |

If any of these cannot be determined from the input, ask the user before proceeding.

For high-dimensional sources, ask these additional required questions before Phase 2:

1. Should dimensions (e.g., country, visa_class, visa_type) be modeled as `attributes` on observations or expanded into many canonical series keys?
2. Is dynamic series-key generation acceptable, or must series remain statically declared in discovery specs?
3. Do downstream APIs need first-class dimension filters now, or is dataset-level retrieval plus client-side filtering acceptable?

### 1b. Validate against platform constraints

Check each of these requirements. If any fail, stop and explain the blocker to the user.

1. **Numeric time series** — The data must be dated decimal observations, not categorical, text, or event data.
2. **Programmatic HTTP access** — The API must return structured responses (JSON or XML) over HTTP. CSV-only or scraping-dependent sources are not viable without user confirmation that they accept the tradeoff.
3. **Maps to canonical schema** — Each observation must map to these required fields:
   - `source_name` (string) — provider identifier
   - `source_type` — must be `"external"` for third-party data
   - `series_key` (string) — canonical hierarchical key
   - `metric_name` (string) — human-readable name
   - `frequency` — one of: `daily`, `weekly`, `monthly`, `quarterly`, `yearly`
   - `date` (ISO date string) — observation date
   - `reported_at` (ISO datetime string) — publication or revision timestamp
   - `value` (numeric string) — the observation value
4. **Stable series identifiers** — The provider must use persistent IDs for each series across API calls.
5. **Free or free-tier access** — No paid commercial licensing. Free API keys requiring registration are fine.

If the source is file-based (XLSX/PDF/CSV downloads discovered via HTML scraping), apply this decision rule:

- Mark status as `NEEDS CLARIFICATION` unless the user explicitly accepts the scraping/file-extraction tradeoff.
- Require a parser reliability plan before implementation: parse-success metrics per file, hard failure thresholds, and row-count sanity checks.

If the source is high-dimensional (for example country x category x class), apply this decision rule:

- Confirm whether product requirements need first-class API filtering by dimensions.
- If yes and the current platform only supports static canonical series discovery, mark `BLOCKED` and explain required platform changes.
- If no, map dimensions into `attributes` and keep a bounded static canonical series set.

### 1c. Check for conflicts

- Read discovered adapter manifests from `apps/pipeline/src/orchestration/jobs/sources/*_source.py` and verify the proposed `source_key` does not collide with any existing `SOURCE_SPEC.source_key`.
- Verify the proposed `canonical_series_keys` do not duplicate any existing canonical keys.

### 1d. Report assessment

Present the feasibility assessment to the user in this format:

```
## Feasibility Assessment: <Provider Name>

**Status**: VIABLE / BLOCKED / NEEDS CLARIFICATION

### Source Profile
<table from 1a>

### Constraint Check
- [x] Numeric time series
- [x] Programmatic HTTP access
- [x] Maps to canonical schema
- [x] Stable series identifiers
- [x] Free access
- [x] No source_key conflict
- [x] No canonical_series_key conflict

### Proposed Record Mapping
source_name: "<PROVIDER>"
source_type: "external"
series_key: "<CATEGORY.COUNTRY.SERIES>"
metric_name: "<Human Name>"
frequency: "<cadence>"
date: <mapping from API field>
reported_at: <mapping from API field>
value: <mapping from API field>

### Notes
<any caveats, assumptions, or decisions made>
```

Wait for user confirmation before proceeding to Phase 2. If the status is BLOCKED, explain what must change. If NEEDS CLARIFICATION, ask specific questions.

---

## Phase 2: Build the Source Adapter

Once the user confirms the assessment, implement the source adapter.

### 2a. Read reference implementation

Read these files to ensure you follow established patterns exactly:

- `apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py` — canonical multi-series adapter
- `apps/pipeline/src/orchestration/jobs/source_ingest_runner.py` — the runner interface your handler calls
- `apps/pipeline/src/orchestration/jobs/workflow_registry.py` — `SourceWorkflowRegistration` dataclass
- `apps/pipeline/src/orchestration/jobs/workflow_request.py` — `SourceWorkflowRequest` schema
- `apps/pipeline/src/orchestration/jobs/workflow_result.py` — `SourceWorkflowResult` schema

### 2b. Create the source module

Create the adapter by running `pnpm run provider:bootstrap -- ...` first, then complete implementation in `apps/pipeline/src/orchestration/jobs/sources/<provider>_<series>_source.py`.

**Critical**: The filename **must** end in `_source.py`. The discovery filter in `discovery.py` enforces this.

The module must export:

1. **Source key constant**: `<PROVIDER>_<SERIES>_SOURCE_KEY = "<provider>_<series>"`

2. **Series configs** (if multi-series): A tuple of dicts, each containing:
   - `series_item_key` — operator-facing series trigger identity
   - `provider_series_id` — the provider's own ID for the series
   - `canonical_series_key` — canonical persistence identity
   - `metric_name` — human name
   - `dataset_description` — short description for discovery
   - `dataset_geographic_scope` — country or region
   - `topic_tags` — list of string tags
   - `frequency` — publication cadence

3. **Client class** (optional Protocol + default implementation): Handles HTTP fetching. Use `urllib.request.urlopen` following the FRED pattern. The client must:
   - Accept configurable base URL and timeout
   - Support date-range or start-date filtering when the API supports it
   - Return parsed observation rows as `list[dict[str, Any]]`

4. **Record mapper function**: `_map_<provider>_records(rows, series_config) -> list[dict[str, object]]`
   Each mapped record must include all fields the canonical normalizer expects:

   ```python
   {
       "source_name": "<PROVIDER>",
       "source_type": "external",
       "series_key": series_config["canonical_series_key"],
       "metric_name": series_config["metric_name"],
       "dataset_title": series_config["metric_name"],
       "dataset_description": series_config["dataset_description"],
       "dataset_geographic_scope": series_config["dataset_geographic_scope"],
       "topic_tags": series_config["topic_tags"],
       "frequency": series_config["frequency"],
       "date": <from API row>,
       "reported_at": <from API row or current UTC>,
       "value": <from API row>,
       "attributes": {"provider_series_id": series_config["provider_series_id"]},
   }
   ```

5. **Builder function**: `build_<provider>_<series>_source_workflow(runner, *, observation_repository, client=None, schedule_policy=None) -> SourceWorkflowRegistration`

   The handler inside must:
   - Check for `request.run_context.get("records")` passthrough (for testing)
   - Resolve credentials from `run_context` then environment variables
   - Return a clear failure result with `outcome_reason_code="missing_credentials"` if auth is required but absent
   - Iterate over series configs, respecting `request.run_context.get("series_item_keys")` filtering
   - Read checkpoints from `observation_repository.read_latest_observed_on(series_key=...)`
   - Fetch, map, and run records through `runner.run_records()`
   - Track per-series outcomes in `series_outcomes`
   - Aggregate counts and determine final status (`success`, `partial_success`, `failure`)
   - Return a `SourceWorkflowRegistration` with:
     - `workflow_id="wf-<provider>-<series>"`
     - `source_key=<SOURCE_KEY_CONSTANT>`
     - `owner="pipeline"`
     - `supported_trigger_modes={"scheduled", "on_demand"}`

Follow the FRED adapter structure closely. Do not invent new patterns.

---

## Phase 3: Standalone Validation

Before wiring into the pipeline, verify the adapter logic works in isolation.

### 3a. Create a standalone test script

Create a temporary test script (not in the test suite — this is a throwaway manual verification). Run it with the pipeline's Python environment.

The script should:

1. **Test record mapping** — Construct sample API response rows (based on real API response structure from the user's input or documentation) and pass them through the mapper function. Verify the output dicts have all required canonical fields with correct types.

2. **Test builder construction** — Call the builder with a mock runner and mock observation repository. Verify it returns a `SourceWorkflowRegistration` with correct `workflow_id`, `source_key`, `status="active"`, and `supported_trigger_modes`.

3. **Test handler with fixture data** — Invoke the handler with a `SourceWorkflowRequest` containing `run_context={"records": [...]}` (passthrough mode). Verify the result has `status="success"` and correct `accepted_count`.

4. **Test credential failure path** — Invoke the handler without credentials and without passthrough records. Verify it returns `status="failure"` with `outcome_reason_code="missing_credentials"` (only for sources that require authentication).

5. **Test parser-loss guardrails** (required for file/PDF extraction sources) — Simulate malformed lines/rows and verify the adapter emits clear failure or quarantine behavior when parse loss exceeds threshold.

Run the script:

```bash
PYTHONPATH=apps/pipeline uv run --project apps/pipeline python <script_path>
```

If any test fails, fix the adapter and re-run until all pass. Then delete the temporary test script.

### 3b. Optional: Live API smoke test

If the user has provided API credentials or the API is open, optionally test a real API call:

```bash
PYTHONPATH=apps/pipeline <ENV_VAR>=<key> uv run --project apps/pipeline python -c "
from src.orchestration.jobs.sources.<module> import _Default<Provider>Client
client = _Default<Provider>Client()
rows = client.fetch_observations(...)
print(f'Fetched {len(rows)} rows')
print(rows[:2])
"
```

Report the result to the user. Do not proceed to Phase 4 if live calls fail unexpectedly.

---

## Phase 4: Pipeline Integration

Implement onboarding in a single adapter module. Do not edit bootstrap orchestration files.

### 4a. Add SOURCE_SPEC in the adapter module

In `apps/pipeline/src/orchestration/jobs/sources/<provider>_<series>_source.py`, add:

```python
SOURCE_SPEC: dict[str, Any] = {
  "source_key": <SOURCE_KEY_CONSTANT>,
  "provider_group_key": "<provider>",
  "series_item_keys": (<tuple_of_series_item_keys>),
  "canonical_series_keys": (<tuple_of_canonical_series_keys>),
  "ownership_mode": "grouped",
  "cron_schedule": "<cron_expression>",
  "cadence_label": "<cadence_label>",
  "builder": build_<provider>_<series>_source_workflow,
}
```

Constraints:

- `series_item_keys` and `canonical_series_keys` must have equal length and matching index order.
- `source_key` must be unique across all adapter modules.
- `cadence_label` must be one of: `hourly`, `daily`, `weekly`, `monthly`, `custom_interval`.
- `cron_schedule` must use valid five-field cron syntax.

### 4b. Verify derived registration surfaces

Discovery, schedules, Dagit assets, and workspace catalog are derived automatically from scanned manifests.
Do not manually edit:

- `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`
- `apps/pipeline/src/orchestration/schedules/source_asset_schedules.py`
- `apps/pipeline/src/orchestration/source_asset_definitions.py`
- `apps/pipeline/src/orchestration/definitions.py`

---

## Phase 5: Verification

Phase 5 has two stages: offline tests (unit/integration tests, lint, typecheck) and live stack verification (Docker Compose environment with Dagster materialization and API validation). Both must pass.

### 5a. Run the dynamic registration tests

```bash
pnpm exec nx run pipeline:test:orchestration:dynamic-registration
```

If this target is not available, fall back to:

```bash
PYTHONPATH=apps/pipeline uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_source_asset_discovery.py apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py apps/pipeline/tests/orchestration/test_definitions_smoke.py -v
```

### 5b. Run the full orchestration test suite

```bash
uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/ -v
```

If tests fail, diagnose and fix. Do not skip or modify existing tests to make them pass — the new provider must be additive and not break existing behavior.

### 5c. Run affected quality gates

```bash
pnpm run affected:lint && pnpm run affected:typecheck
```

Fix any lint or type errors in your new code.

### 5d. Start the local Docker Compose stack

The local development environment runs five services via Docker Compose: PostgreSQL (`db` on port 55432), the backend API (`backend` on port 8080), Dagit (`dagit` on port 3001), the frontend (`frontend` on port 3000), and a pipeline placeholder. All services mount the workspace directory, so your code changes are already visible inside the containers.

**Step 1 — Bring up the stack and wait for health checks:**

```bash
docker compose up -d
```

**Step 2 — Wait for the DB and Dagit services to become healthy.** Poll container health rather than sleeping a fixed duration. The DB must be healthy before migrations can run; Dagit must be healthy before you can materialize assets.

```bash
# Wait for DB to become healthy (up to 60s)
for i in $(seq 1 60); do
  db_healthy=$(docker compose ps db --format json | grep -c '"Health":"healthy"' || true)
  if [[ "$db_healthy" -gt 0 ]]; then
    echo "DB healthy after ${i}s"
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "DB did not become healthy within 60s" >&2
    docker compose logs db >&2
    exit 1
  fi
  sleep 1
done
```

**Step 3 — Run database migrations** so the schema is current:

```bash
bash tools/quality/local-stack/run-db-migrations.sh
```

**Step 4 — Wait for Dagit to become healthy** (can take longer due to workspace loading):

```bash
# Wait for Dagit to become healthy (up to 180s)
for i in $(seq 1 180); do
  dagit_healthy=$(docker compose ps dagit --format json | grep -c '"Health":"healthy"' || true)
  if [[ "$dagit_healthy" -gt 0 ]]; then
    echo "Dagit healthy after ${i}s"
    break
  fi
  if (( i % 30 == 0 )); then
    echo "Still waiting for Dagit health: ${i}s elapsed"
  fi
  if [[ "$i" -eq 180 ]]; then
    echo "Dagit did not become healthy within 180s" >&2
    docker compose logs dagit >&2
    exit 1
  fi
  sleep 1
done
```

**Step 5 — Wait for the backend API to become healthy:**

```bash
for i in $(seq 1 60); do
  if curl -fsS http://localhost:8080/api/health >/dev/null 2>&1; then
    echo "Backend API healthy after ${i}s"
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "Backend API did not become healthy within 60s" >&2
    docker compose logs backend >&2
    exit 1
  fi
  sleep 1
done
```

**Step 6 — Verify the Dagit workspace loaded correctly** and the new assets are visible:

```bash
bash tools/quality/local-stack/test-dagit-endpoint.sh
```

This runs a GraphQL query against Dagit to confirm the workspace has loaded location entries. If it fails, check `docker compose logs dagit` for import errors — a common cause is a syntax error or missing import in the source adapter.

### 5e. Materialize the new assets via Dagit GraphQL

Trigger asset materialization for each new series using the Dagster GraphQL API. The Dagit service inside Docker listens on port 3000 internally but is mapped to port 3001 on the host.

**For each new asset** (identified by `key_prefix` and `name` from Phase 4c), execute a materialization:

```bash
# Replace <provider_group> and <series_name> with actual values.
# Repeat this block for each new asset.

DAGIT_URL="http://localhost:3001"
ASSET_KEY='["<provider_group>", "<series_name>"]'

# Launch the asset materialization run
LAUNCH_RESPONSE=$(curl -fsS -X POST "${DAGIT_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"mutation LaunchAssetRun(\$assetKeys: [AssetKeyInput!]!) { launchPipelineExecution(executionParams: { mode: \\\"default\\\", executionMetadata: { tags: [{ key: \\\"dagster/step_selection\\\", value: \\\"*\\\" }] }, selector: { assetSelection: \$assetKeys } }) { __typename ... on LaunchRunSuccess { run { runId status } } ... on PythonError { message } ... on RunConfigValidationInvalid { errors { message } } } }\",
    \"variables\": { \"assetKeys\": [{\"path\": ${ASSET_KEY}}] }
  }")

echo "Launch response: ${LAUNCH_RESPONSE}"
```

Extract the `runId` from the response. If the launch returned a `PythonError` or `RunConfigValidationInvalid`, the materialization could not start — read the error message, diagnose, and fix before retrying.

### 5f. Monitor the run to completion

Poll the run status until it reaches a terminal state. Runs typically complete within 30–60 seconds for API-backed sources.

```bash
RUN_ID="<runId from launch response>"
DAGIT_URL="http://localhost:3001"

for i in $(seq 1 120); do
  RUN_RESPONSE=$(curl -fsS -X POST "${DAGIT_URL}/graphql" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"query RunStatus(\$runId: ID!) { runOrError(runId: \$runId) { __typename ... on Run { runId status } ... on PythonError { message } } }\",
      \"variables\": { \"runId\": \"${RUN_ID}\" }
    }")

  RUN_STATUS=$(echo "$RUN_RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
run = data.get('data', {}).get('runOrError', {})
print(run.get('status', 'UNKNOWN'))
" 2>/dev/null || echo "PARSE_ERROR")

  echo "Run ${RUN_ID} status: ${RUN_STATUS} (${i}s)"

  case "$RUN_STATUS" in
    SUCCESS)
      echo "Materialization completed successfully."
      break
      ;;
    FAILURE|CANCELED)
      echo "Materialization ended with status: ${RUN_STATUS}" >&2
      break
      ;;
    PARSE_ERROR)
      echo "Could not parse run status response" >&2
      echo "$RUN_RESPONSE" >&2
      break
      ;;
    *)
      # QUEUED, STARTING, STARTED, etc. — still in progress
      ;;
  esac

  if [[ "$i" -eq 120 ]]; then
    echo "Run did not complete within 120s" >&2
    break
  fi
  sleep 1
done
```

### 5g. Check run logs for errors

If the run status is `FAILURE`, fetch the structured run event logs to diagnose the problem:

```bash
RUN_ID="<runId>"
DAGIT_URL="http://localhost:3001"

LOG_RESPONSE=$(curl -fsS -X POST "${DAGIT_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"query RunLogs(\$runId: ID!) { logsForRun(runId: \$runId) { __typename ... on EventConnection { events { __typename message ... on ExecutionStepFailureEvent { stepKey error { message stack } } } } } }\",
    \"variables\": { \"runId\": \"${RUN_ID}\" }
  }")

# Extract failure events
echo "$LOG_RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
events = data.get('data', {}).get('logsForRun', {}).get('events', [])
failures = [e for e in events if e.get('__typename') == 'ExecutionStepFailureEvent']
if not failures:
    print('No step failure events found.')
    # Print last 10 log messages for context
    for e in events[-10:]:
        print(f'  [{e.get(\"__typename\", \"?\")}] {e.get(\"message\", \"\")}')
else:
    for f in failures:
        print(f'STEP FAILED: {f.get(\"stepKey\", \"?\")}')
        err = f.get('error', {})
        print(f'  Message: {err.get(\"message\", \"\")}')
        stack = err.get('stack', [])
        if stack:
            print('  Stack trace (last 5 frames):')
            for line in stack[-5:]:
                print(f'    {line.rstrip()}')
"
```

**If the run failed:**

1. Read the error message and stack trace.
2. Common failure causes:
   - **`missing_credentials`**: The source requires an API key. If the user has provided one, pass it as an environment variable to the Dagit container: stop the stack, add the variable to `docker-compose.yml` under the `dagit` service's `environment` section (or use `docker compose run -e <VAR>=<VALUE>`), and retry.
   - **Import errors**: A typo in the source module or missing import in `discovery.py`. Fix and restart: `docker compose restart dagit`.
   - **Contract validation failures**: The mapped records don't satisfy `CanonicalObservation` validation. Fix the record mapper and retry.
   - **Network errors**: The provider API is unreachable from inside the Docker container. Verify DNS resolution and network access from the container.
3. After fixing, restart the affected container (`docker compose restart dagit` if code changed, or `docker compose restart backend` if backend-only) and re-run from step 5e.

**If the run succeeded**, proceed to 5h.

### 5h. Verify data appears in the discovery API

After a successful materialization, the ingested observations should be visible through the backend API. Query each endpoint to confirm.

**Check 1 — Search for the new dataset:**

```bash
# URL-encode the search term (use a distinctive word from the metric_name or topic_tags)
SEARCH_TERM="<distinctive_keyword>"

SEARCH_RESPONSE=$(curl -fsS "http://localhost:8080/api/datasets/search?q=${SEARCH_TERM}")

echo "$SEARCH_RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', [])
print(f'Search returned {len(items)} result(s)')
for item in items:
    print(f'  - {item.get(\"dataset_id\", \"?\")} | {item.get(\"title\", \"?\")} | {item.get(\"source_name\", \"?\")}')
if not items:
    print('WARNING: No search results. Check that dataset_title and topic_tags were emitted correctly.')
"
```

If no results are returned, this means either:

- The records were not persisted (check run logs)
- The search index fields (`dataset_title`, `dataset_description`, `topic_tags`) were empty or missing in the mapped records — go back and fix the record mapper

**Check 2 — Verify the dataset appears in recent updates:**

```bash
RECENT_RESPONSE=$(curl -fsS "http://localhost:8080/api/datasets/recent?limit=10")

echo "$RECENT_RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', [])
print(f'Recent updates: {len(items)} dataset(s)')
for item in items:
    print(f'  - {item.get(\"dataset_id\", \"?\")} | {item.get(\"title\", \"?\")} | reported_at={item.get(\"latest_reported_at\", \"?\")}')
"
```

The new dataset should appear near the top since it was just ingested. If it doesn't appear at all, the `reported_at` timestamps may be missing or malformed.

**Check 3 — Fetch dataset detail and verify observations:**

Use the `dataset_id` from the search or recent response to fetch the full detail:

```bash
DATASET_ID="<dataset_id from search or recent response>"

DETAIL_RESPONSE=$(curl -fsS "http://localhost:8080/api/datasets/${DATASET_ID}")

echo "$DETAIL_RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Dataset: {data.get(\"title\", \"?\")}')
print(f'Description: {data.get(\"description\", \"?\")}')
print(f'Geographic scope: {data.get(\"geographic_scope\", \"?\")}')
print(f'Source: {data.get(\"source_name\", \"?\")}')
tags = data.get('topic_tags', [])
print(f'Topic tags: {tags}')
obs = data.get('observations', [])
print(f'Observations: {len(obs)} point(s)')
if obs:
    print(f'  First: date={obs[0].get(\"date\", \"?\")} value={obs[0].get(\"value\", \"?\")}')
    print(f'  Last:  date={obs[-1].get(\"date\", \"?\")} value={obs[-1].get(\"value\", \"?\")}')
if not obs:
    print('WARNING: No observations returned. Check that date and value fields were mapped correctly.')
"
```

**Validate the detail response against these expectations:**

| Field              | Expected                                                                        |
| ------------------ | ------------------------------------------------------------------------------- |
| `title`            | Non-empty, matches `dataset_title` / `metric_name` from the record mapper       |
| `description`      | Non-empty, matches `dataset_description` from the record mapper                 |
| `geographic_scope` | Non-empty, matches `dataset_geographic_scope` from the record mapper            |
| `source_name`      | Matches the `source_name` constant in the adapter (e.g. `"BLS"`, `"WORLDBANK"`) |
| `topic_tags`       | Non-empty list, matches the `topic_tags` list from the series config            |
| `observations`     | At least 1 observation with valid `date` and numeric `value`                    |

If any field is missing or wrong, trace it back through the chain: record mapper output → canonical normalizer → persistence → query projection. Fix the root cause (almost always in the record mapper) and re-run from 5e.

**Check 4 — Verify catalog listing:**

```bash
CATALOG_RESPONSE=$(curl -fsS "http://localhost:8080/api/datasets?group_by_source=true")

echo "$CATALOG_RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', [])
# Look for the new provider group
for item in items:
    source = item.get('source_name', '')
    print(f'  Source: {source} | datasets: {len(item.get(\"datasets\", [item]))}')
"
```

Confirm the new provider appears as a source group in the catalog.

### 5i. Tear down or preserve the stack

After verification is complete:

- If all checks passed, bring the stack down:
  ```bash
  docker compose down
  ```
- If you need to debug further, leave the stack running and tell the user:
  - Dagit UI: `http://localhost:3001`
  - Backend API: `http://localhost:8080`
  - Frontend: `http://localhost:3000`
  - DB: `localhost:55432` (user: `longtail`, password: `longtail`, database: `longtail_local`)

### 5j. Report results

Present the final status:

```
## Provider Onboarded: <Provider Name>

### Files Created
- `apps/pipeline/src/orchestration/jobs/sources/<file>.py`

### Files Modified
- `apps/pipeline/src/orchestration/jobs/sources/<file>.py` (plus tests)

### Series Registered
| Series Item Key | Canonical Key | Frequency | Schedule |
|---|---|---|---|
| <key> | <canonical> | <freq> | <cron> |

### Offline Verification
- [ ] Dynamic registration tests: PASSED
- [ ] Full orchestration suite: PASSED
- [ ] Lint + typecheck: PASSED

### Live Stack Verification
- [ ] Docker Compose stack healthy (db, dagit, backend)
- [ ] DB migrations applied
- [ ] Dagit workspace loaded with new assets
- [ ] Asset materialization run: SUCCESS (run_id: <id>)
- [ ] No errors in run logs
- [ ] Dataset appears in search API (`/api/datasets/search`)
- [ ] Dataset appears in recent updates (`/api/datasets/recent`)
- [ ] Dataset detail has correct metadata and observations (`/api/datasets/<id>`)
- [ ] Dataset appears in catalog (`/api/datasets?group_by_source=true`)
- [ ] Stack torn down cleanly
```

---

## Error Handling

- **If the user's description is too vague**: Ask specific questions about the API endpoint, response format, and series to ingest. Do not guess at API structure.
- **If the API requires authentication the user hasn't provided**: Complete Phases 1–4 and offline tests (5a–5c) using the passthrough/mock testing path. For live stack verification (5d–5h), ask the user for the credential. If they cannot provide one, skip live verification and note it clearly in the final report. Do not add secrets to `docker-compose.yml` permanently — use `docker compose run -e <VAR>=<VALUE>` or instruct the user to set the variable.
- **If existing tests break**: This means you introduced a regression. Read the failing test, understand what it asserts, and fix your code. Never modify existing tests to accommodate new code.
- **If the canonical schema doesn't fit**: Explain the mismatch to the user. Do not modify `canonical_observation.py` or the normalizer — those are shared contracts. If the data genuinely cannot map, report it as a blocker in Phase 1.
- **If the Docker Compose stack fails to start**: Check `docker compose logs <service>` for the failing service. Common issues: port conflicts (another process on 55432, 8080, 3001, or 3000), stale volumes (`docker compose down -v` to reset), or missing Docker daemon.
- **If Dagit workspace fails to load after your changes**: This almost always means an import error in the new source module or in `discovery.py`. Run `docker compose logs dagit 2>&1 | tail -50` to see the Python traceback. Fix the import, then `docker compose restart dagit` and re-wait for health.
- **If materialization succeeds but the API returns no data**: The backend reads from PostgreSQL. Verify migrations ran (`bash tools/quality/local-stack/check-db-revision.sh`). Then check that the `CanonicalIngestService` actually persisted rows by querying the DB directly: `docker compose exec db psql -U longtail -d longtail_local -c "SELECT COUNT(*) FROM observations;"`. If rows exist but the API doesn't return them, restart the backend: `docker compose restart backend`.
