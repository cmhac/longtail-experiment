# Contract: FRED Interest Rate Source

**Feature**: 008-add-fred-source  
**Owner**: apps/pipeline source orchestration stack

## Source Workflow Registration Contract

### Source Identity

- `source_key`: `fred_fedfunds`
- `workflow_id`: stable workflow identifier for runtime registration
- `supported_trigger_modes`: `scheduled`, `on_demand`

### Handler Input

The source handler receives one workflow request object containing:

| Field          | Type   | Description                         |
| -------------- | ------ | ----------------------------------- |
| `run_id`       | string | Orchestration run identity          |
| `source_key`   | string | Source identity                     |
| `trigger_type` | enum   | Scheduled or on-demand mode         |
| `run_context`  | object | Optional execution context metadata |

### Handler Output

The source handler returns one workflow result object containing:

| Field                 | Type    | Description                                |
| --------------------- | ------- | ------------------------------------------ |
| `source_key`          | string  | Source identity                            |
| `status`              | enum    | `success`, `partial_success`, or `failure` |
| `accepted_count`      | integer | Count of accepted records                  |
| `quarantined_count`   | integer | Count of contract-rejected records         |
| `failed_count`        | integer | Count of processing failures               |
| `outcome_reason_code` | string? | Optional reason code for failure modes     |
| `message`             | string? | Optional operator-friendly message         |

## Credential Contract

- Environment variable name: `FRED_API_KEY`
- Local source of truth for developer workflows: `docker/compose/local.secrets.env`
- If credential is missing or empty, handler must fail with explicit configuration error signal.

## Provider Request Contract

### Request Requirements

- Use configured provider base endpoint.
- Include API key credential for authorization.
- Include target series identifier for federal funds interest rate data.
- Include start-date parameter for incremental fetch where available.

### Response Expectations

Provider response must include observation items containing date/value fields.
Rows that do not satisfy required fields or numeric parsing constraints are rejected through canonical validation paths.

## Canonical Ingest Contract

The source adapter must emit payloads consumable by canonical ingest service with required keys:

- `source_name`
- `source_type`
- `series_key`
- `metric_name`
- `frequency`
- `date`
- `reported_at`
- `value`

Optional metadata is allowed via additional attributes fields, provided canonical schema permits it.

## Persistence Contract

- Canonical ingest repository must perform idempotent upsert by `(series_key, observed_on)`.
- Successful upserts must make observations queryable for incremental checkpoint derivation.
- Persistence failures must propagate to workflow result accounting as failure or partial-success according to existing runner semantics.

## Observability Contract

- Missing credential errors are operator-visible and distinguishable from provider/network errors.
- Provider/network failures map to deterministic reason codes for troubleshooting.
- Quarantine counts and failure counts are reflected in run summary output.
