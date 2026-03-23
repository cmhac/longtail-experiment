# Data Model: Real Backend Discovery API Runtime

## Overview

This feature preserves canonical persisted entities and updates runtime read projections and verification evidence so discovery endpoints are always served from persisted records. Fixture entities are test-only and excluded from runtime startup paths.

## Entities

### 1) RuntimeDiscoveryDataSource

Represents the active discovery data source used by backend runtime startup.

Fields:

- mode: enum (required; `persisted` or `test_fixture`)
- startup_context: enum (required; `runtime`, `test`)
- allowed: boolean (required)

Validation rules:

- When `startup_context=runtime`, `mode` MUST be `persisted`.
- When `mode=test_fixture`, `startup_context` MUST be `test`.
- Any runtime fixture selection is invalid.

Relationships:

- One RuntimeDiscoveryDataSource governs one runtime service composition.

### 2) PersistedDatasetProjection

Represents a discovery-level dataset projection assembled from persisted records.

Fields:

- dataset_id: string (required)
- source_name: string (required)
- title: string (required)
- description: string (optional)
- geographic_scope: string (optional)
- topic_tags: list[string] (required)
- latest_update_at: datetime (optional)

Validation rules:

- `dataset_id` must be canonical and stable across surfaces.
- `topic_tags` is always present; empty list allowed.
- Projection values must originate from persisted tables.

Relationships:

- One PersistedDatasetProjection maps to one DatasetDetailProjection by dataset_id.

### 3) DatasetDetailProjection

Represents dataset detail metadata plus chronologically ordered observations.

Fields:

- dataset_id: string (required)
- metadata: map[string, string | number | boolean | null] (optional)
- observations: list[ObservationPoint] (required)

Validation rules:

- Unknown `dataset_id` resolves to explicit not-found.
- Known dataset with zero observations returns empty observations list.
- `observations` are deterministic and chronological.

Relationships:

- One DatasetDetailProjection contains many ObservationPoint records.

### 4) ObservationPoint

Represents one persisted observation in detail responses.

Fields:

- observed_on: date (required)
- value: decimal (required)
- reported_at: datetime (required)
- attributes: map[string, string | number | boolean | null] (optional)

Validation rules:

- Provenance and timestamp semantics must match canonical persisted records.
- Tie-break behavior for same-day observations is deterministic.

Relationships:

- Many ObservationPoint records belong to one DatasetDetailProjection.

### 5) VerificationRunEvidence

Represents captured evidence proving ingest-to-API parity and runtime fixture prohibition.

Fields:

- run_id: string (required)
- ingest_event_detected: boolean (required)
- endpoint_delta_detected: boolean (required)
- runtime_fixture_paths_detected: integer (required; expected 0)
- command_outputs: list[string] (required)

Validation rules:

- `endpoint_delta_detected=true` is required after persisted ingest change.
- `runtime_fixture_paths_detected` must be zero in runtime verification.

Relationships:

- One VerificationRunEvidence record references one end-to-end verification flow.

## State Transitions

### Runtime Startup Data Source Selection

1. requested: runtime startup initiated.
2. validated: startup context and source mode validated.
3. composed: discovery service composed from persisted repository.
4. serving: endpoints respond from persisted records.

Transition constraints:

- Any fixture mode during runtime blocks transition from requested to composed.
- Missing persisted schema readiness blocks transition from validated to composed.

### Ingest-to-API Parity Verification

1. baseline_captured: pre-ingest API response captured.
2. ingest_applied: persisted records changed via ingest.
3. parity_checked: post-ingest API response evaluated.
4. verified: response delta confirms persisted-data sourcing.

Transition constraints:

- If no response delta is observed after ingest change, verification fails.
- If runtime fixture path is detected, verification fails.

## Invariants

- Runtime discovery responses are sourced from persisted records only.
- Fixture-backed discovery sources are test-only and never in runtime startup.
- Endpoint shapes and explicit not-found semantics remain stable.
- Discovery and detail ordering remains deterministic for identical inputs.
