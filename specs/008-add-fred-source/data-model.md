# Data Model: FRED Interest Rate Source

**Feature**: 008-add-fred-source

## Entities

### FredSourceConfig (runtime, non-persisted)

Configuration context for FRED source execution.

| Field             | Type    | Required | Notes                                                           |
| ----------------- | ------- | -------- | --------------------------------------------------------------- |
| `source_key`      | string  | Yes      | Constant identifier for workflow registration (`fred_fedfunds`) |
| `series_id`       | string  | Yes      | Provider series identifier used in API requests                 |
| `api_key`         | string  | Yes      | Read from local secret env context                              |
| `base_url`        | string  | Yes      | Provider API root                                               |
| `timeout_seconds` | integer | Yes      | Request timeout boundary                                        |

Validation rules:

- `api_key` must be non-empty at runtime.
- `series_id` must be provider-valid.

---

### ExternalInterestRateObservation (source payload, pre-normalization)

One raw provider observation record returned by FRED before canonical mapping.

| Field            | Type   | Required | Notes                                   |
| ---------------- | ------ | -------- | --------------------------------------- |
| `date`           | string | Yes      | Observation period date from provider   |
| `value`          | string | Yes      | Numeric text that must parse to decimal |
| `realtime_start` | string | No       | Optional provider revision metadata     |
| `realtime_end`   | string | No       | Optional provider revision metadata     |

Validation rules:

- Records with non-parseable numeric values are rejected/quarantined.
- Records missing required date/value are rejected.

---

### CanonicalObservation (contract entity, persisted)

Normalized observation consumed by canonical ingest service and persisted through repository boundary.

| Field                   | Type     | Required | Notes                                  |
| ----------------------- | -------- | -------- | -------------------------------------- |
| `series_key`            | string   | Yes      | Stable domain series identity          |
| `metric_name`           | string   | Yes      | Human-readable metric label            |
| `frequency_granularity` | enum     | Yes      | Daily/monthly/etc. canonical frequency |
| `source_type`           | string   | Yes      | External source classification         |
| `observed_on`           | date     | Yes      | Observation period                     |
| `reported_at`           | datetime | Yes      | Source publication/retrieval timestamp |
| `value`                 | decimal  | Yes      | Canonical numeric value                |
| `attributes`            | object   | No       | Source metadata extension map          |

Validation rules:

- `(series_key, observed_on)` must remain unique for upsert semantics.
- `value` must conform to canonical numeric constraints.

---

### ObservationStore Tables (new in migration 0004)

Durable schema required to support canonical observation queries and incremental checkpoints.

#### data_series

| Column                  | Type        | Nullable | Notes                      |
| ----------------------- | ----------- | -------- | -------------------------- |
| `series_key`            | string      | No       | Primary business key       |
| `source_name`           | string      | No       | Provider/source identifier |
| `metric_name`           | string      | No       | Display metric label       |
| `frequency_granularity` | string      | No       | Canonical frequency        |
| `attributes`            | json/object | Yes      | Optional metadata          |
| `updated_at`            | timestamptz | No       | Last mutation time         |

#### observations

| Column        | Type        | Nullable | Notes                        |
| ------------- | ----------- | -------- | ---------------------------- |
| `series_key`  | string      | No       | FK to `data_series`          |
| `observed_on` | date        | No       | Period key                   |
| `reported_at` | timestamptz | No       | Source report/retrieval time |
| `value`       | numeric     | No       | Canonical measure            |
| `created_at`  | timestamptz | No       | Insert timestamp             |
| `updated_at`  | timestamptz | No       | Upsert timestamp             |

Primary/unique expectation:

- Unique key on `(series_key, observed_on)` for idempotent upsert.

## Relationships

1. One `FredSourceConfig` defines one source workflow registration.
2. One run fetches many `ExternalInterestRateObservation` rows.
3. Each raw row maps to one `CanonicalObservation` (or quarantine outcome).
4. One `data_series` row has many `observations` rows.

## State Transitions

1. Source configured with valid credential -> source eligible for execution.
2. Source executes -> provider rows fetched.
3. Row normalizes successfully -> canonical upsert into observation store.
4. Row normalization fails -> quarantined/failure counters updated.
5. Next run checkpoint uses latest persisted `observed_on` to drive incremental fetch window.
