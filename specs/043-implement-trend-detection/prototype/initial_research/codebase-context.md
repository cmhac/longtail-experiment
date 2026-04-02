# Codebase Context: Data & Pipeline Research for Trend Detection

**Date gathered**: 2026-03-31  
**Branch**: `042-dataset-comparison-overlay`  
**Purpose**: Pre-planning context for a new trend detection feature

---

## 1. Database Schema

### 1.1 `source_profiles` — Data Provider Registry

Represents one external or internal data provider (e.g. FRED, EIA, NY Fed).

| Column        | Type         | Constraints      | Notes                                                               |
| ------------- | ------------ | ---------------- | ------------------------------------------------------------------- |
| `id`          | UUID         | PK               |                                                                     |
| `source_key`  | String(255)  | UNIQUE, NOT NULL | Stable machine slug, e.g. `fred_fedfunds`, `eia_retail_fuel_prices` |
| `source_name` | String(255)  | UNIQUE, NOT NULL | Display name, e.g. `FRED`                                           |
| `source_type` | String(64)   | NOT NULL         | `external` or `internal`                                            |
| `title`       | String(255)  | NOT NULL         | Human-readable title                                                |
| `description` | String(2048) | NOT NULL         | Free-text description                                               |
| `created_at`  | DateTime(tz) | NOT NULL         |                                                                     |

**Indexes**: unique on `source_key`, unique on `source_name`.  
Added in migration `0010_source_profile_metadata` (current HEAD).

---

### 1.2 `data_series` — Individual Time Series / Datasets

Each row represents one logical time series with its own observation history. This is the central entity that trend detection would operate on.

| Column              | Type          | Constraints                         | Notes                                                                                                                                                       |
| ------------------- | ------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | UUID          | PK                                  |                                                                                                                                                             |
| `source_profile_id` | UUID          | FK → `source_profiles.id`, NOT NULL |                                                                                                                                                             |
| `series_key`        | String(255)   | UNIQUE, NOT NULL                    | Canonical series identifier used as `dataset_id` throughout; e.g. `INT.US.FEDFUNDS`, `ENERGY.US.GASREGW`, `LABOR.US.NYFED.RECENT_COLLEGE_GRAD_UNEMPLOYMENT` |
| `metric_name`       | String(255)   | NOT NULL                            | Short metric label, e.g. `Effective Federal Funds Rate`                                                                                                     |
| `title`             | String(255)   | NOT NULL                            | Display title                                                                                                                                               |
| `description`       | Text          | nullable                            | Human-readable description                                                                                                                                  |
| `geographic_scope`  | String(255)   | nullable                            | e.g. `United States`                                                                                                                                        |
| `default_scale`     | Numeric(10,4) | NOT NULL, default 1                 | Rendering scale hint                                                                                                                                        |
| `created_at`        | DateTime(tz)  | NOT NULL                            |                                                                                                                                                             |

**Indexes**:

- `ix_data_series_title_lower` on `title` with `text_pattern_ops` (for LIKE prefix search)
- `ix_data_series_source_profile_id_title` on `(source_profile_id, title)` (discovery sort)

**Key fact**: `series_key` is the stable cross-system join key. API payloads use `series_key` as `dataset_id`. The pipeline uses `series_key` as the deduplication key on upserts. Any trend-detection results should also key on `series_key`.

---

### 1.3 `observations` — The Time Series Data Points

The primary data table for trend detection. Each row is one dated measurement for one series.

| Column        | Type          | Constraints                     | Notes                                                                                                                                   |
| ------------- | ------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `id`          | UUID          | PK                              |                                                                                                                                         |
| `series_id`   | UUID          | FK → `data_series.id`, NOT NULL |                                                                                                                                         |
| `observed_on` | Date          | NOT NULL                        | Calendar date of measurement — the **primary chronological axis**                                                                       |
| `value`       | Numeric(20,8) | NOT NULL                        | The observed float value with high precision                                                                                            |
| `reported_at` | DateTime(tz)  | NOT NULL                        | When the observation was ingested/published — secondary sort only                                                                       |
| `attributes`  | JSONB         | NOT NULL, default `{}`          | Free-form key/value pairs; carries `unit_type` (`usd`, `percent`, `number`), `unit` label strings, and other provider-specific metadata |

**Unique constraint**: `uq_observation_series_date` on `(series_id, observed_on)` — **exactly one canonical value per series per date**. Revisions replace the old row (tracked in `revision_records`).

**Indexes**:

- `ix_observations_series_id_reported_at` on `(series_id, reported_at)`
- `ix_observations_series_id_observed_on` on `(series_id, observed_on)`

**Key fact**: The `value` column is `Numeric(20,8)` in the DB but cast to Python `float` at the API boundary. Trend computations should operate on float-cast values as they are served.

---

### 1.4 `topic_tags` and `data_series_topic_tags` — Discovery Taxonomy

Normalized many-to-many tag labels attached to series.

**`topic_tags`**:
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tag_name` | String(128) | UNIQUE; lowercase normalized, e.g. `interest rates`, `monetary policy`, `energy`, `labor` |
| `created_at` | DateTime(tz) | |

**`data_series_topic_tags`** (junction table):
| Column | Type | Notes |
|---|---|---|
| `data_series_id` | UUID | FK → `data_series.id` CASCADE |
| `topic_tag_id` | UUID | FK → `topic_tags.id` CASCADE |

Index on `topic_tag_id` for efficient tag-to-dataset lookups.

---

### 1.5 `category_nodes` and `geography_nodes` — Hierarchical Taxonomy

Self-referential hierarchy trees. Used for browse-by-category and browse-by-geography pages.

Both tables follow the same structure:
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `code` | String(64) | UNIQUE |
| `name` | String(255) | |
| `parent_id` | UUID | nullable self-FK |
| `is_global` | Boolean | `geography_nodes` only — marks non-geographic entries |

---

### 1.6 `provenance_records` — Immutable Observation Source Metadata

One-to-many off `observations`. Each observation may have one or more provenance records (source URL, release ID, ingested timestamp).

| Column              | Type         | Notes                            |
| ------------------- | ------------ | -------------------------------- |
| `id`                | UUID         | PK                               |
| `observation_id`    | UUID         | FK → `observations.id`           |
| `source_release_id` | String(128)  | Provider-side release identifier |
| `source_url`        | String(1024) | Origin URL                       |
| `ingested_at`       | DateTime(tz) |                                  |

---

### 1.7 `revision_records` — Observation Revision Lineage

Links a superseded observation to its replacement, enabling lineage tracing when a provider revises a historical data point.

| Column                      | Type        | Notes                     |
| --------------------------- | ----------- | ------------------------- |
| `id`                        | UUID        | PK                        |
| `superseded_observation_id` | UUID        | FK → `observations.id`    |
| `current_observation_id`    | UUID        | FK → `observations.id`    |
| `reason`                    | String(255) | Free-text revision reason |

Check constraint: `ck_revision_distinct_observations` — superseded ≠ current.

---

### 1.8 Ingestion Runtime Tables

These track orchestration state and are **not relevant to trend analysis**:

- **`ingestion_runs`**: Per-run lifecycle counters (`accepted_count`, `quarantined_count`, `failed_count`, `deferred_source_count`, etc.)
- **`source_schedule_policies`**: Per-source cadence state, `last_successful_at`, `next_eligible_at`
- **`source_run_locks`**: Per-source active/queued overlap guard

---

## 2. Ingested Data Sources

Three active external source adapters are currently registered, each declaring a cron schedule and a list of canonical series.

### 2.1 FRED (Federal Reserve Economic Data)

- **Source key**: `fred_fedfunds`
- **Provider group key**: `fred`
- **API**: `api.stlouisfed.org` using `FRED_API_KEY` env var
- **Series**:
  | `series_item_key` | `canonical_series_key` | `metric_name` | `unit_type` | Cadence |
  |---|---|---|---|---|
  | `fred_fedfunds` | `INT.US.FEDFUNDS` | Effective Federal Funds Rate | `percent` | Monthly |
  | `fred_gasregw` | `ENERGY.US.GASREGW` | US Regular Gas Price | `usd` | Monthly |
- **Topic tags**: `interest rates`, `monetary policy`, `federal reserve`, `energy`, `gasoline`, `consumer prices`

### 2.2 EIA (US Energy Information Administration)

- **Source key**: `eia_retail_fuel_prices`
- **Provider group key**: `eia`
- **API**: `api.eia.gov/v2/petroleum/pri/gnd/data` using `EIA_API_KEY` env var; paginated (`page_size=5000`)
- **Products**: Multiple petroleum product codes × geography (`duoarea`) combinations
- **Cadence**: Weekly
- **Unit type**: Numeric (dollar-denominated fuel prices)

### 2.3 NY Fed College Labor Market

- **Source key**: `nyfed_college_labor_market`
- **Provider group key**: `nyfed`
- **API**: Excel workbook download from newyorkfed.org (no API key required)
- **Parsing**: `polars` for Excel ingestion; two sheets: `unemployed` and `underemployed`
- **Series** (4 total):
  | `series_item_key` | `canonical_series_key` | `metric_name` | `unit_type` | Cadence |
  |---|---|---|---|---|
  | `nyfed_recent_graduate_unemployment` | `LABOR.US.NYFED.RECENT_COLLEGE_GRAD_UNEMPLOYMENT` | Recent College Graduates Unemployment Rate | `percent` | Monthly |
  | `nyfed_college_graduate_unemployment` | `LABOR.US.NYFED.COLLEGE_GRAD_UNEMPLOYMENT` | College Graduates Unemployment Rate | `percent` | Monthly |
  | `nyfed_recent_graduate_underemployment` | `LABOR.US.NYFED.RECENT_COLLEGE_GRAD_UNDEREMPLOYMENT` | Recent College Graduates Underemployment Rate | `percent` | Monthly |
  | `nyfed_college_graduate_underemployment` | `LABOR.US.NYFED.COLLEGE_GRAD_UNDEREMPLOYMENT` | College Graduates Underemployment Rate | `percent` | Monthly |
- **Topic tags**: `labor`, `unemployment`, `underemployment`, `college graduates`, `recent graduates`, `ny fed`

---

## 3. Canonical Observation Schema (`CanonicalObservation`)

All pipeline sources normalize their output into a `CanonicalObservation` Pydantic model before persistence:

```python
class CanonicalObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_key: str          # e.g. "fred_fedfunds"
    source_name: str         # e.g. "FRED"
    source_title: str        # e.g. "Federal Reserve Economic Data"
    source_description: str
    source_type: str         # "external" | "internal"
    series_key: str          # e.g. "INT.US.FEDFUNDS"
    metric_name: str
    dataset_title: str | None
    dataset_description: str | None
    dataset_geographic_scope: str | None
    topic_tags: list[str]
    observed_on: date
    reported_at: datetime
    value: Decimal
    unit: str | None         # e.g. "Percent", "Dollars per Gallon"
    unit_type: Literal["usd", "percent", "number"] | None
    attributes: dict[str, str]   # free-form metadata pass-through
```

---

## 4. How Observations Are Queried (Backend API)

### 4.1 Detail API Call Chain

`GET /api/datasets/{dataset_id}` with optional `from_date` / `to_date` query params:

1. `dataset_detail_query.py` → `DatasetDiscoveryService.get_dataset_detail()`
2. → `PersistedDatasetDiscoveryRepository.get_dataset_detail(dataset_id)` — loads metadata row
3. → `PersistedDatasetDiscoveryRepository.list_dataset_observations(dataset_id, from_date, to_date)` — executes:
   ```sql
   SELECT o.observed_on, o.value, o.reported_at, o.attributes
   FROM observations o
   JOIN data_series ds ON ds.id = o.series_id
   WHERE ds.series_key = :dataset_id
     [AND o.observed_on >= :from_date]
     [AND o.observed_on <= :to_date]
   ORDER BY o.observed_on ASC, o.reported_at ASC
   ```
4. `_resolve_dataset_unit_type()` — infers `unit_type` from: `metadata.unit_type` → observation `attributes.unit_type` → label heuristics (`%`, `$`, `dollar`, `percent`)
5. Returns `DatasetDetailResponse` with `observations` as `list[DatasetObservationPoint]`

### 4.2 API Response Shape for Observations

```json
{
  "dataset_id": "INT.US.FEDFUNDS",
  "source": { "id": "fred_fedfunds", "name": "Federal Reserve Economic Data" },
  "title": "Effective Federal Funds Rate",
  "description": "...",
  "geographic_scope": "United States",
  "topic_tags": ["interest rates", "monetary policy", "federal reserve"],
  "metadata": {
    "metric_name": "Effective Federal Funds Rate",
    "unit_type": "percent",
    "source_key": "fred_fedfunds",
    ...
  },
  "observations": [
    {
      "observed_on": "2024-01-01",
      "value": 5.33,
      "reported_at": "2024-01-05T12:00:00+00:00",
      "attributes": { "unit_type": "percent" }
    }
  ],
  "observation_sort": "observed_on_asc,reported_at_asc"
}
```

### 4.3 Dataset Discovery Metadata Query

The `_load_dataset_rows()` SQL join — used for search, catalog, recency, and source/topic pages — collects per-series metadata with latest update timestamp:

```sql
SELECT
    ds.series_key AS dataset_id,
    sp.source_key, sp.source_name, sp.title AS source_title,
    sp.description AS source_description, sp.source_type,
    ds.metric_name, ds.title, ds.description, ds.geographic_scope,
    COALESCE(ARRAY_AGG(DISTINCT tt.tag_name ORDER BY tt.tag_name)
        FILTER (WHERE tt.tag_name IS NOT NULL), ARRAY[]::text[]) AS topic_tags,
    MAX(o.reported_at) AS latest_update_at
FROM data_series ds
JOIN source_profiles sp ON sp.id = ds.source_profile_id
LEFT JOIN data_series_topic_tags dstt ON dstt.data_series_id = ds.id
LEFT JOIN topic_tags tt ON tt.id = dstt.topic_tag_id
LEFT JOIN observations o ON o.series_id = ds.id
GROUP BY ds.id, ds.series_key, sp.source_key, ...
```

---

## 5. Relevant Recently Implemented Features

### 5.1 Spec 041 — Relative Change Visualization (frontend-only)

Adds the ability to switch the dataset detail chart from raw observed values to signed percentage change computed as:

```
((current_value - baseline_value) / baseline_value) × 100
```

Two baseline modes:

- **Rolling**: each point compared to a prior observation offset (1, 2, 3, … n observations ago)
- **Fixed**: all points compared to one constant baseline observation (selected by exact available date or by observation index)

**Key constraints established by this spec**:

- Computations are done client-side in the frontend using the already-fetched observation array
- Non-computable points (zero baseline, insufficient history) are rendered as timeline gaps — no coercion
- Observation chronological order is the calculation basis
- `unit_type` drives axis/tooltip formatting

### 5.2 Spec 042 — Dataset Comparison Overlay (frontend-only)

Adds multi-dataset overlay on a single chart with:

- Browser-local comparison set (max 5 datasets)
- Union-of-dates timeline (gaps for missing dates)
- Unit compatibility checks (incompatible units → auto-switch to relative mode)
- Shared relative baseline configuration across all compared series
- Stable per-session color mapping

**Key constraints established by this spec**:

- No new backend or database changes — all computation is client-side
- Observation data is fetched independently per dataset using the existing detail API

---

## 6. Dagster Pipeline Architecture

### 6.1 Dagster `Definitions` (`src/orchestration/definitions.py`)

The workspace module is `src.orchestration.definitions`. It wires:

```python
defs = Definitions(
    assets=SOURCE_DAGIT_ASSETS,     # per-series-item Dagster assets
    jobs=[ingest_job],              # single universal ingest job
    schedules=SOURCE_ASSET_SCHEDULES,   # per-source cron schedules
    sensors=[ondemand_sensor],      # cursor-based on-demand trigger
    resources=_INGEST_RUNTIME.dagit_resources(),
)
```

All of these are **dynamically discovered** at import time from `src/sources/*_source.py` modules — no hardcoded lists.

### 6.2 The Single Job: `ingest_job`

All execution routes through one Dagster job with one op (`execute_ingest_run`). The op reads run tags to determine trigger type and source/series selection:

- `trigger_type` tag: `"scheduled"` or `"on_demand"`
- `source_keys` tag: comma-separated source keys to run (or all registered sources)
- `series_item_keys` tag: specific series within a source (or all series for selected sources)
- `requested_by` tag: identity of the trigger (e.g. `fred_fedfunds_schedule`, `ondemand_sensor`)

### 6.3 Execution Flow

```
ingest_job
└── execute_ingest_run (Dagster op)
      ├── reads run tags
      ├── validates source_keys against registered sources
      ├── resolves series selection
      └── RunCoordinator.run()
            ├── reads SourceSchedulePolicy from PostgresRunRepository
            ├── DueSourceSelector.evaluate_on_demand() or .evaluate_scheduled()
            │     → produces SourceEligibilityDecision list
            ├── builds due_source_keys list
            ├── ParallelSourceExecutor.execute()
            │     max_active_sources=4 (ThreadPoolExecutor)
            │     for each due source (FIFO launch order):
            │       ├── SourceLockService.acquire()  ← `source_run_locks` table
            │       ├── source adapter handler()
            │       │     └── SourceIngestRunner.run_records()
            │       │           ├── validates each record via CanonicalIngestService
            │       │           └── PostgresObservationRepository.persist()
            │       │                 ├── UPSERT source_profiles (ON CONFLICT source_key)
            │       │                 ├── UPSERT data_series (ON CONFLICT series_key)
            │       │                 ├── UPSERT/sync topic_tags
            │       │                 └── UPSERT observations (ON CONFLICT series_id, observed_on)
            │       └── SourceLockService.release()
            └── RunOutcomeService → writes IngestionRun counters to DB
```

### 6.4 Per-Source Schedules

Each source adapter manifest declares `cron_schedule` and `cadence_label`. `source_asset_schedules.py` auto-generates a Dagster `@schedule` for each:

| Schedule name                         | Cron             | Cadence |
| ------------------------------------- | ---------------- | ------- |
| `fred_fedfunds_schedule`              | e.g. `0 0 1 * *` | Monthly |
| `eia_retail_fuel_prices_schedule`     | e.g. `0 6 * * 1` | Weekly  |
| `nyfed_college_labor_market_schedule` | e.g. `0 0 1 * *` | Monthly |

Each `RunRequest` carries `source_keys`, `series_item_keys`, and `trigger_type="scheduled"` tags.

### 6.5 Per-Series-Item Dagster Assets

`source_asset_definitions.py` creates a `@asset` per `series_item_key`:

- Asset key: `{provider_group_key}/{series_item_short_name}` (e.g. `fred/fedfunds`)
- Materializing an asset sends an on-demand `RunCoordinator.run()` for just that series
- Visible and triggerable in Dagit UI

### 6.6 On-Demand Sensor

`ondemand_sensor` polls a cursor for an operator-set token. When a cursor is found:

- Clears the cursor
- Emits a `RunRequest` with `trigger_type="on_demand"`, `source_selection_mode="operator_requested"`
- No specific `source_keys` — runs all registered sources

### 6.7 Infrastructure: Two PostgreSQL Databases

| Role                 | DB               | Port (local) | Tables                                                                                                  |
| -------------------- | ---------------- | ------------ | ------------------------------------------------------------------------------------------------------- |
| **Canonical data**   | `longtail_local` | 55432        | `source_profiles`, `data_series`, `observations`, `topic_tags`, provenance, revision, ingestion runtime |
| **Dagster metadata** | `dagster_local`  | 55433        | Dagster run storage, event log, schedule state (managed by `dagster_postgres`)                          |

`dagster.yaml` configures three Dagster backends — `run_storage`, `event_log_storage`, `schedule_storage` — all pointing to `dagster_db` via env vars.

### 6.8 Dagit Docker Compose Service

The `dagit` service:

1. Writes `dagster.yaml` to `DAGSTER_HOME`
2. Runs `uv sync --project apps/pipeline --frozen`
3. Starts `dagster dev -d apps/pipeline -m src.orchestration.definitions`
4. Healthcheck verifies Dagit HTTP reachability AND workspace load via GraphQL

---

## 7. Properties of the Data Relevant to Trend Detection

### 7.1 Observation Cadence Is Irregular and Unknown at the Schema Level

The `frequency_granularity` column on `source_profiles` was **dropped** in migration `0009_drop_source_profile_frequency`. There is no stored per-series frequency in the current schema. Cadence must be inferred from observation date spacing at query time, or supplied by a new schema field.

Current series cadences in practice:

- EIA retail fuel prices: **weekly**
- FRED Fed Funds Rate: **monthly**
- FRED Regular Gas Price: **monthly**
- NY Fed college labor metrics: **monthly**

### 7.2 One Canonical Value Per (series, date)

`uq_observation_series_date` guarantees exactly one live observation value per series per date. Revisions flow through `revision_records` but result in the observations table being updated in-place. Trend algorithms always operate on the current canonical set of observations.

### 7.3 Value Precision

- DB: `Numeric(20,8)` — 8 decimal places of precision
- API boundary: cast to Python `float` (64-bit)
- Trend computations should work from the float-cast values

### 7.4 Chronological Order Is the Primary Axis

`observed_on` (Date) is the time axis. Observations are always sorted `observed_on ASC, reported_at ASC` when served. The `reported_at` timestamp is a publication metadata field, not a meaningful time axis for analysis.

### 7.5 `unit_type` Is Inferred, Not a Dedicated Column

`unit_type` (`usd` | `percent` | `number`) is resolved at query time via a priority chain:

1. `data_series` / dataset metadata dict `unit_type` field
2. Observation `attributes` JSONB `unit_type` key
3. Heuristic inference from `unit` label strings (`%`, `$`, `dollar`, `percent`)

There is no dedicated normalized `unit_type` column on `data_series`. Trend analysis that is unit-type-aware (e.g., displaying trends as "percentage points" for `percent` series vs. "$X" for `usd` series) needs to use the same resolution logic.

### 7.6 Cross-Series Comparison Is the Direct Predecessor Feature

Spec 042 just added client-side multi-series comparison using union-of-dates. Spec 041 added client-side relative-change computation. Both operate on the same `observations` array already fetched from the API. Trend detection is a natural extension of this computation layer, and could either:

- Run client-side on already-fetched data (consistent with 041 and 042 approach), or
- Pre-compute results server-side/in pipeline and expose via a new API endpoint

### 7.7 `series_key` Is the Cross-System Identifier

`series_key` (e.g. `INT.US.FEDFUNDS`) is the stable join key between:

- The Dagster pipeline (source adapter output)
- The `data_series` table
- The backend API (`dataset_id` in all payloads)
- The frontend (URL params, comparison set storage)

Any trend detection results — whether stored in DB or computed and referenced by API — should key on `series_key`.

---

## 8. Extension Points for Trend Detection

### 8.1 Frontend Client-Side (consistent with specs 041 and 042)

- Compute trends in the browser from already-fetched `observations` arrays
- No new pipeline or backend changes needed
- Natural fit for rolling-window statistics (moving average, rolling std dev)
- Limitation: cannot pre-compute or persist signals

### 8.2 Backend API Endpoint (new query layer)

- New endpoint that reads `observations` for one or more series and returns computed trend signals
- Lives in `apps/backend/src/query/` following existing service/repository patterns
- Could be called live by the frontend alongside the existing detail API
- Needs a new repository method and service orchestration layer

### 8.3 Pre-Computed Pipeline Job (new Dagster job)

- New Dagster job (separate from `ingest_job`) triggered after ingest completes
- Reads `observations` for affected series, computes trend signals, writes to a new DB table
- Triggered by: a new `@sensor` downstream of `ingest_job`, a schedule, or an asset downstream of source assets
- Requires a new Alembic migration for the trend signal storage table
- Consistent with the existing source-asset pattern; new jobs are added following the same wiring in `definitions.py`

### 8.4 Downstream Asset Pattern

- Add a `@asset` per series that consumes the ingested observation asset and produces trend output
- Materializes automatically when upstream source assets are materialized
- Visible in Dagit as a derived asset (e.g. `fred/fedfunds_trend`)
- Requires new DB table for persistence

---

## 9. Current Migration State

Migration head: `0010_source_profile_metadata`

Full migration history:
| Revision | Description |
|---|---|
| `0001_contract_baseline` | Initial `source_profiles`, `ingestion_runs` baseline |
| `0002_ingestion_runtime_and_conflicts` | Conflict tracking tables |
| `0003_source_schedule_and_eligibility` | `source_schedule_policies`, `source_run_locks` |
| `0004_observation_store` | Creates `data_series` and `observations` tables |
| `0005_source_asset_schedule_cutover` | Schedule authority migration |
| `0006_series_ownership_transition` | Multi-series adapter ownership |
| `0007_dataset_metadata_and_topic_tags` | Adds `title`, `description`, `geographic_scope` to `data_series`; creates `topic_tags` and `data_series_topic_tags` |
| `0008_dataset_discovery_indexes` | Discovery read-path indexes |
| `0009_drop_source_profile_frequency` | Drops `frequency_granularity` column from `source_profiles` |
| `0010_source_profile_metadata` | Adds `source_key`, `title`, `description` to `source_profiles` |

A trend detection feature requiring persistence would need migration `0011`.
