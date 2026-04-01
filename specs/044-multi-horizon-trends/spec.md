# Feature Specification: Multi-Horizon Trends

**Feature Branch**: `044-multi-horizon-trends`
**Created**: 2026-04-01
**Status**: Draft
**Input**: User description: "We want to surface multi-horizon trend signals on dataset detail pages. Instead of the current simplified trend overlay approach, the pipeline should compute trend snapshots across multiple fixed lookback windows (e.g. 1M, 6M, 1Y, 5Y) and persist them. The backend should expose a canonical trend descriptor per dataset (the authoritative weighted signal plus individual lookback snapshots). The frontend should replace the existing ad-hoc trend overlay with a compact, reusable trend chip that reads from the canonical backend payload."

## Clarifications

### Session 2026-04-01

- Q: Which lookback windows should be supported? → A: Fixed windows matching the existing range filter keys: 1M, 6M, 1Y, 5Y. ALL-time is excluded from snapshot computation because it depends on dataset age.
- Q: How should the canonical trend descriptor be computed from multiple lookback snapshots? → A: Weighted combination across available lookback windows; longer windows receive higher weight. Weighting algorithm and version must be versioned and deterministic.
- Q: What trend classifications are supported per snapshot? → A: `rising`, `falling`, `stable`, `insufficient_data`.
- Q: When a lookback window contains insufficient observations to compute a trend, what happens? → A: That snapshot is classified as `insufficient_data` and excluded from canonical weighting.
- Q: Should lookback snapshots be recomputed on every ingest run? → A: Yes, recomputed and persisted as part of a backfill/reclassification job after each ingest cycle.
- Q: What happens to existing trend overlay UI components on the frontend? → A: `TrendOverlayLayer` and `TrendTooltipController` are removed; the new `DatasetTrendChip` reads from the canonical backend payload only.
- Q: Is the canonical trend descriptor included in the existing dataset detail API response or a separate endpoint? → A: Embedded in the existing dataset detail response (`DatasetDetailResponse`) as an optional field, and also available as a dedicated lookback snapshot endpoint.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Pipeline Computes Multi-Lookback Trend Snapshots (Priority: P1)

As a data pipeline operator, I want the ingest pipeline to evaluate and persist trend snapshots across multiple fixed lookback windows so that authoritative trend signals are always available for downstream consumption.

**Why this priority**: Without computed and persisted lookback snapshots there is no backend payload and no frontend signal to display. This is the foundational pipeline block.

**Independent Test**: Run the trend backfill service against a dataset with sufficient history and verify `lookback_trend_snapshots` rows are written for each applicable window; datasets with insufficient history receive `insufficient_data` classifications.

**Acceptance Scenarios**:

1. **Given** a dataset with at least 30 days of observations, **When** the trend backfill job runs, **Then** one lookback snapshot row is persisted per applicable window (1M, 6M, 1Y, 5Y) with a classification and confidence value.
2. **Given** a dataset with fewer observations than required for a lookback window, **When** the trend backfill job runs, **Then** that window's snapshot is classified as `insufficient_data` and written with `confidence: null`.
3. **Given** a prior snapshot set exists for a dataset, **When** the backfill job runs again after new data is ingested, **Then** the existing snapshots are replaced with freshly computed values.
4. **Given** multiple datasets exist, **When** the backfill job runs, **Then** snapshots are written for all eligible datasets without cross-contamination.

---

### User Story 2 - Backend Serves Canonical Trend Descriptor (Priority: P2)

As an API consumer, I want the dataset detail response to include a canonical trend descriptor (weighted authoritative signal) and the individual lookback snapshots so I can display structured multi-horizon trend information without recomputing it client-side.

**Why this priority**: The backend must serve the canonical payload before the frontend can render it.

**Independent Test**: Fetch a dataset detail response and confirm `trend.canonical` includes a weighted direction and version string; `trend.lookbacks` includes one entry per computed window with `window`, `direction`, and `confidence` fields.

**Acceptance Scenarios**:

1. **Given** a dataset with computed lookback snapshots, **When** a client fetches the dataset detail endpoint, **Then** the response includes a `trend` object with `canonical` (weighted descriptor) and `lookbacks` (per-window snapshots).
2. **Given** a dataset with no computed snapshots, **When** a client fetches the dataset detail endpoint, **Then** the `trend` field is present but `canonical` is `null` and `lookbacks` is an empty array.
3. **Given** a lookback snapshot with `insufficient_data` classification, **When** the backend assembles the canonical descriptor, **Then** that window is excluded from the weighted computation.
4. **Given** the canonical descriptor is computed, **When** a client reads `trend.canonical.weighting_version`, **Then** the value is a non-empty version string matching the current weighting implementation.

---

### User Story 3 - Frontend Renders Canonical Trend Chip (Priority: P3)

As a dataset viewer, I can see a compact canonical trend chip on the dataset detail page that reflects the authoritative multi-horizon signal so I can quickly understand the overall trend direction without interpreting raw chart data.

**Why this priority**: The frontend is the user-facing surface and depends on both US1 and US2 being complete.

**Independent Test**: Open a dataset detail page that has computed trend snapshots; verify the `DatasetTrendChip` renders a direction badge and that hovering or expanding it reveals per-window lookback results; verify that pages for datasets with no snapshots render an `insufficient data` state without breaking.

**Acceptance Scenarios**:

1. **Given** a dataset detail page with a computed canonical trend descriptor, **When** the viewer loads the page, **Then** the `DatasetTrendChip` displays the canonical direction (`rising`, `falling`, or `stable`) with appropriate visual styling.
2. **Given** the canonical direction chip is visible, **When** the viewer inspects the chip, **Then** individual lookback windows (1M, 6M, 1Y, 5Y) and their classifications are accessible.
3. **Given** a dataset with no computed trend, **When** the viewer loads the detail page, **Then** the chip renders an `—` or `no trend data` placeholder without error.
4. **Given** the old `TrendOverlayLayer` and `TrendTooltipController` components have been removed, **When** the detail chart renders, **Then** no import errors or broken overlay references appear.

### Edge Cases

- What happens when all lookback windows are `insufficient_data`? The canonical descriptor returns `null` direction and the chip shows an unavailable state.
- What happens when the weighting algorithm changes? The `weighting_version` field must change so consumers can detect stale cached values.
- What happens if only some windows are available (e.g. dataset is less than 1Y old)? Only available windows contribute to the canonical weighting; shorter-horizon windows dominate.
- What happens during backfill if the pipeline is interrupted mid-run? Snapshots for datasets not yet processed retain prior values; rerunning the job brings them up to date.
- What happens if the frontend receives a `trend` payload with an unrecognized `direction` value? The chip renders an unknown/unavailable state rather than crashing.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The pipeline MUST compute trend snapshots for each of the fixed lookback windows (1M, 6M, 1Y, 5Y) per dataset after each ingest cycle.
- **FR-002**: Each lookback snapshot MUST record `window`, `direction` (`rising` | `falling` | `stable` | `insufficient_data`), `confidence` (float or null), and `computed_at` timestamp.
- **FR-003**: The pipeline MUST persist a canonical trend descriptor per dataset that aggregates available lookback snapshots using a deterministic, versioned weighting algorithm.
- **FR-004**: The canonical descriptor MUST record `direction`, `confidence`, `weighting_version`, and `computed_at`.
- **FR-005**: The backend dataset detail endpoint MUST include a `trend` field with `canonical` and `lookbacks` in its response payload.
- **FR-006**: When a dataset has no snapshots, the `trend.canonical` MUST be `null` and `trend.lookbacks` MUST be an empty array.
- **FR-007**: The frontend MUST replace `TrendOverlayLayer` and `TrendTooltipController` with a `DatasetTrendChip` component that reads from the `trend` payload.
- **FR-008**: The `DatasetTrendChip` MUST render a canonical direction badge and surface per-window lookback data.
- **FR-009**: The `DatasetTrendChip` MUST handle null/absent `trend` gracefully with a visible unavailable state.

### Non-Functional Requirements

- **NFR-001**: Lookback snapshot computation MUST be deterministic for the same input observations.
- **NFR-002**: The weighting algorithm MUST be identified by a version string that changes whenever the computation logic changes.
- **NFR-003**: Snapshot writes MUST be idempotent (re-running the backfill for the same dataset produces the same result given the same observations).
- **NFR-004**: The backend must return the `trend` field within the existing dataset detail latency budget (no additional round-trip; data is read from pre-computed rows).
- **NFR-005**: Coverage for the `trend_analysis` library and all modified backend/frontend modules MUST remain at or above 90%.

### Out of Scope

- Real-time trend recomputation on every API request (trends are pre-computed by the pipeline).
- User-configurable lookback windows (windows are fixed per the agreed set).
- Trend email/alerting integration (separate feature).
- Trend data in the dataset list/search pages (detail page only for this feature).
