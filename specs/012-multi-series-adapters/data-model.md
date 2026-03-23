# Data Model: Multi-Series Source Adapter Model

## Overview

This feature introduces explicit ownership and operability concepts for series that may be grouped under one provider adapter or split across multiple adapters.

## Entities

### 1) ProviderGroup

Represents one external provider domain and its logical grouping boundary.

Fields:

- provider_group_key: string (required, unique)
- provider_name: string (required)
- ownership_default_mode: enum { grouped, split } (required)
- is_active: boolean (required)
- description: string (optional)

Validation rules:

- provider_group_key must be stable and immutable once published.
- ownership_default_mode must be one of grouped or split.

Relationships:

- One ProviderGroup has many SeriesItems.

### 2) SeriesItem

Represents one independently identifiable dataset/series under a provider group.

Fields:

- series_item_key: string (required, unique)
- provider_group_key: string (required)
- canonical_series_key: string (required, unique)
- provider_series_identifier: string (required)
- display_name: string (required)
- frequency_hint: string (optional)
- schedule_owner_key: string (required)
- is_active: boolean (required)

Validation rules:

- series_item_key and canonical_series_key must be globally unique.
- active series must have a non-empty schedule_owner_key.

Relationships:

- Many SeriesItems belong to one ProviderGroup.
- One SeriesItem has many SeriesExecutionOutcomes.

### 3) AdapterOwnershipMode

Defines whether a series executes under grouped provider adapter ownership or a split dedicated adapter.

Fields:

- series_item_key: string (required, unique)
- mode: enum { grouped, split } (required)
- owner_adapter_key: string (required)
- effective_from: timestamp (required)
- effective_to: timestamp (optional)
- transition_reason: string (optional)

Validation rules:

- At most one active mode record per series at a time.
- effective ranges must not overlap for the same series.

Relationships:

- One SeriesItem has many historical AdapterOwnershipMode records.

### 4) SeriesExecutionOutcome

Captures outcome details for one series execution slice regardless of grouped or split ownership.

Fields:

- run_id: string (required)
- series_item_key: string (required)
- source_key: string (required)
- trigger_origin: string (required)
- status: enum { success, partial_success, failure, deferred, not_due } (required)
- accepted_count: integer (required, >= 0)
- quarantined_count: integer (required, >= 0)
- failed_count: integer (required, >= 0)
- outcome_reason_code: string (optional)
- failure_summary: string (optional)
- started_at: timestamp (required)
- completed_at: timestamp (required)

Validation rules:

- completed_at must be >= started_at.
- counts must be non-negative.
- status must align with count semantics (for example failure with no accepted_count).

Relationships:

- Many SeriesExecutionOutcomes can share one run_id.
- Many SeriesExecutionOutcomes can belong to one series_item_key.

## State Transitions

### Series ownership lifecycle

1. grouped_active: series belongs to grouped adapter ownership.
2. transition_pending: ownership change prepared with overlap safeguards.
3. split_active: series ownership moved to dedicated adapter.
4. retired: series inactive and not scheduled.

Transition constraints:

- grouped_active -> split_active requires duplicate-trigger guard validation.
- split_active -> grouped_active requires explicit owner reassignment and schedule cleanup.
- Any active state -> retired requires disabled schedule ownership.

## Invariants

- Every active series must have exactly one active ownership mode.
- Every series run outcome must map to a single series_item_key.
- Grouped and split ownership must never produce simultaneous scheduled execution for the same series item and cadence window.
- Provider grouping metadata must remain queryable for all series outcomes.
