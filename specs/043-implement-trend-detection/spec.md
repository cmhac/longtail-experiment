# Feature Specification: End-to-End Trend Detection

**Feature Branch**: `043-implement-trend-detection`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "Ok, we're gonna create a new spec for this work. The goal here is going to be to fully implement trend detection, from the actual data processing/trend identification library we'll build, to where it will run in the pipeline, record trends in the database, serves them through the api, and shows them in the ui. as I implied, the data processing will be a new python library we'll create in libs/. it'll be imported by the pipeline code and integrated into our pipeline. Each time new observation is recorded for a dataset, we should run trend detection on that data. if a significant trend is identified, we should store that as a record in the database. we should store past trends as we identify them, including their start and end period, and whether they are ongoing or not. We'll do that by checking for existing current trends, rerunning the trend detection, seeing if it's different, etc. we'll need to be careful about seasonality - if a trend was originally classified as non-seasonal or seasonal and that classification changes, we should immediately error that run in the pipeline. We'll need to wire this into the database and backend API, and then integrate this into the UI. that'll happen in several places. first, in the recent updates feed, we'll intermix the recent dataset updates and newly-identified trends. then, we'll also have in the dataset detail page, an area that highlights, in green for upward trends and red for downwrad trends, where trends are occurring in the data on the chart. when those highlighted areas are hovered, we should see a tooltip similar to the one we use on the lines on the chart, showing some details about the trend. we currently ahve an unused tab in the top nav for trends, we'll remove that."

## Clarifications

### Session 2026-03-31

- Q: What exact rule should define when an existing ongoing trend is considered “different” and must be ended/replaced? → A: Replace trend when top-level label changes, OR when direction/strength/seasonality changes in the persisted trend signature.
- Q: When a dataset currently has an ongoing trend, but a new run finds no significant trend, what should happen to the ongoing trend record? → A: End the ongoing trend record at the latest observation and leave the dataset with no ongoing trend.
- Q: For ordering trend events in the unified recent updates feed, which timestamp should represent a trend event? → A: Use trend start period.
- Q: If seasonality classification changes during trend processing, should the failure block only that dataset’s trend write or fail the entire ingestion run? → A: Fail only that dataset’s trend processing, keep recording observation data, and keep trend processing clearly separate from core ingestion in the DAG.
- Q: At first rollout, how much historical trend data should be populated for existing datasets? → A: Perform full historical backfill only when the series has sufficient data and currently has zero trend records; execute this in the first pipeline trend-processing run for that series.
- Q: For the trend classification library, where should thresholds and cadence window settings come from at runtime? → A: Hardcoded defaults in library code only.
- Q: When a series lacks enough observations for reliable trend detection, what should the library return for persistence flow? → A: Return a distinct insufficient_data outcome and skip trend-record writes for that run.
- Q: Should the trend classification library perform any record reads/writes or app-level logic? → A: No. The library must remain pure analysis functions only, with no record IO and no application orchestration logic.
- Q: How should the library communicate algorithm/version identity so pipeline decisions remain reproducible over time? → A: Analysis version is coupled to library version only; any analysis-version change requires a new library release and a manual full re-run/re-backfill of all datasets for consistency.
- Q: When observation spacing is irregular or cadence cannot be inferred confidently, how should the library behave? → A: Treat this the same as seasonality-change handling: fail fast and report an explicit error.
- Q: For the pure trend library, what reproducibility guarantee should be required when running the same input series twice under the same library version? → A: Exact deterministic output match across repeated runs.
- Q: In the pipeline, at what point should trend processing be invoked for a series during a source workflow run? → A: Trend processing should be implemented as its own Dagster asset and run as a downstream task after data fetch/update completion.
- Q: If a downstream trend asset fails for one dataset/series, what DAG failure scope should apply? → A: Fail only the affected source branch/asset chain, while allowing other independent source branches/assets to continue.
- Q: When a source branch is retried after a trend-asset failure, what idempotency boundary should be guaranteed for trend history writes? → A: Use state-based idempotency: retries over identical persisted observation state must not create additional lifecycle records.
- Q: For the downstream trend asset, what should define the processing unit emitted by upstream fetch/update work? → A: Execute trend processing per updated series, driven by upstream emitted series updates.
- Q: For per-series downstream trend execution, how should non-write outcomes be reported for insufficient_data or no_significant_trend? → A: Mark execution successful with explicit no-op outcome metadata, and write no trend lifecycle rows when no lifecycle transition is required.
- Q: For trend details on mobile/touch devices where hover is unavailable, how should chart trend details be revealed? → A: Single tap on a trend span opens a pinned tooltip, and tapping elsewhere closes it.
- Q: How should trend direction remain distinguishable for color-blind users beyond red/green alone? → A: Use dual encoding with color plus distinct fill pattern and direction icon/marker.
- Q: When trend spans are close together on the chart, how should overlap and tooltip concurrency be handled? → A: Trend spans must never overlap, and only one tooltip may be visible at a time.
- Q: For unified recent updates feed trend events, how should deep-link navigation into dataset detail behave? → A: Navigate to dataset detail default view with no trend-focused URL state.
- Q: When trend span data is missing or malformed for dataset detail, how should the UI behave? → A: Hard-fail the detail page and show an error state instead of rendering the chart.

## User Scenarios & Testing _(mandatory)_

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Persist Current and Historical Trends (Priority: P1)

As a data platform operator, I need trend detection to run whenever new observations are ingested so that meaningful trends are continuously identified and stored with historical continuity.

**Why this priority**: Trend persistence is the core business capability. Without reliable detection and storage, API and UI features have no trustworthy trend data to present.

**Independent Test**: Can be fully tested by ingesting new observations for one dataset and verifying that current trend state and historical trend lifecycle records are correctly created or updated.

**Acceptance Scenarios**:

1. **Given** a dataset receives new observations and a significant trend is detected, **When** trend detection executes, **Then** a current trend record is stored with start period and ongoing status.
2. **Given** a dataset already has an ongoing trend and a newly detected trend differs materially, **When** trend processing executes, **Then** the prior trend is ended with an end period and a new ongoing trend record is created.
3. **Given** a dataset already has an ongoing trend and the newly detected trend is unchanged, **When** trend processing executes, **Then** no duplicate historical segment is created.
4. **Given** a dataset has an established seasonality classification, **When** a subsequent run changes that classification for the same ongoing trend context, **Then** trend processing for that dataset fails with an explicit error while core observation ingestion remains successful.

---

### User Story 2 - Serve Trends Through Discovery API and Feed (Priority: P2)

As an application consumer, I need trend events and current trend context to be available through discovery APIs so that trend information can be consumed consistently across product surfaces.

**Why this priority**: API delivery enables downstream UI behavior and keeps trend interpretation centralized instead of fragmented client logic.

**Independent Test**: Can be tested by calling discovery endpoints after trend records exist and validating that recent updates responses include both dataset updates and trend events in expected ordering.

**Acceptance Scenarios**:

1. **Given** trend records exist for one or more datasets, **When** recent updates are requested, **Then** trend events and dataset updates are returned in one unified feed ordered by recency.
2. **Given** a dataset has active and historical trend records, **When** dataset detail is requested, **Then** trend metadata needed for chart highlighting and tooltip content is included.

---

### User Story 3 - Visualize Trends in UI (Priority: P3)

As an end user exploring datasets, I want trend periods highlighted directly on the dataset chart and visible in the recent updates feed so I can quickly identify where meaningful upward and downward trends occurred.

**Why this priority**: Visualization improves decision speed and comprehension, but it depends on persisted trend data and API payload updates from P1 and P2.

**Independent Test**: Can be tested by opening dataset detail and discovery feed views after seeded trend records and verifying color-coded trend overlays, hover details, and navigation cleanup behavior.

**Acceptance Scenarios**:

1. **Given** a dataset has upward and downward trend segments, **When** the dataset detail chart loads, **Then** upward trend spans are visually highlighted in green and downward spans in red.
2. **Given** a user hovers a highlighted trend span on desktop or taps a trend span on touch devices, **When** the tooltip appears, **Then** it shows trend details aligned with existing chart tooltip interaction patterns.
3. **Given** the top navigation includes an unused trends tab, **When** this feature is released, **Then** that unused tab is removed.

---

### Edge Cases

- New observations are ingested for a dataset with too few points to evaluate trend significance.
- Multiple ingestion events for the same dataset occur close together and attempt concurrent trend updates.
- Existing trend history contains a malformed or overlapping segment boundary from legacy/backfill data.
- Trend significance drops below threshold and no replacement significant trend is identified.
- Seasonality classification changes for one dataset while other datasets in the same ingestion run remain valid.
- A series has no trend records yet but also lacks sufficient historical observations for full backfill.
- Observation spacing is irregular and cadence inference is ambiguous or invalid.
- API requests ask for dataset detail or recent updates while trend records are absent for some datasets.
- UI receives trend spans that partially extend outside the currently visible chart window.
- Incoming trend span payloads may contain boundaries that would overlap and must be normalized to non-overlapping display regions.
- Dataset detail trend span payload may be missing or malformed and must trigger a deterministic UI error state.
- Touch-only devices must still access full trend tooltip details without hover.
- Users with color-vision deficiencies must distinguish upward and downward trend spans without relying on hue alone.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST evaluate trend state for a dataset whenever new observations are persisted for that dataset.
- **FR-002**: System MUST persist trend outcomes as time-bounded records that include trend direction, significance context, trend start period, optional trend end period, and ongoing status.
- **FR-003**: System MUST preserve historical trend continuity by ending prior ongoing records when a materially different significant trend is detected and creating a new ongoing record.
- **FR-003a**: System MUST treat a trend as materially different when either the top-level trend label changes or any persisted trend-signature dimension changes (direction, strength, or seasonality classification).
- **FR-004**: System MUST avoid creating duplicate historical trend segments when trend classification remains unchanged across runs.
- **FR-004a**: System MUST end an ongoing trend at the latest available observation when a subsequent run finds no significant trend and MUST leave the dataset with no ongoing trend record.
- **FR-005**: System MUST fail trend processing for the affected dataset when seasonality classification for a continuing trend context changes between runs, while allowing core observation ingestion for that dataset and other datasets to continue.
- **FR-006**: System MUST ensure trend writes are idempotent for repeated processing of the same observation state.
- **FR-007**: System MUST expose persisted trend information through backend discovery responses needed by recent updates and dataset detail experiences.
- **FR-008**: System MUST intermix trend events with dataset updates in the recent updates feed response, using a single recency ordering model.
- **FR-008a**: System MUST use trend start period as the ordering timestamp for trend events in the unified recent updates feed.
- **FR-009**: System MUST provide dataset detail trend span data sufficient to render chart overlays and hover details.
- **FR-010**: System MUST render upward trend spans in green and downward trend spans in red on the dataset detail chart.
- **FR-010a**: System MUST apply a second, non-color encoding for trend direction (distinct fill pattern and/or direction icon/marker) so upward and downward trend spans remain distinguishable without relying on hue alone.
- **FR-011**: System MUST present trend details using interaction behavior consistent with existing chart tooltips, including hover on desktop and tap-to-pin on touch devices.
- **FR-011a**: System MUST allow at most one active trend tooltip at a time across chart interactions.
- **FR-012**: System MUST remove the unused trends tab from top-level navigation.
- **FR-013**: System MUST keep non-trend discovery and dataset detail behaviors unchanged when no trend data exists.
- **FR-013a**: System MUST navigate trend feed item clicks to dataset detail default view without requiring trend-focused URL state, preselection, or chart auto-focus.
- **FR-013b**: System MUST render a dataset-detail error state (instead of the chart) when required trend span payload data is missing or malformed for a trend-enabled dataset response.
- **FR-014**: System MUST maintain auditable provenance of trend record lifecycle transitions (created, ended, ongoing).
- **FR-015**: System MUST keep trend processing as a distinct DAG path from core observation ingestion so that trend-processing failures do not block observation persistence.
- **FR-016**: System MUST execute a full historical trend backfill for a series only when both conditions are true: the series has zero existing trend records and the series has sufficient historical observations for trend detection.
- **FR-017**: System MUST skip full historical backfill for a series that has insufficient historical observations, and MUST continue with forward-only trend processing from newly ingested observations.
- **FR-018**: System MUST use only hardcoded in-library default thresholds and cadence window settings at runtime, with no external runtime configuration source.
- **FR-019**: System MUST return a distinct insufficient_data analysis outcome when observations are below required sufficiency thresholds and MUST skip trend-record writes for that dataset in that run.
- **FR-020**: System MUST keep the trend classification library pure and side-effect free, with no database reads, no database writes, and no application orchestration logic.
- **FR-021**: System MUST restrict record reads/writes, lifecycle decisions, and DAG control flow to pipeline/application layers that consume library outputs.
- **FR-022**: System MUST couple analysis version identity to the released library version rather than storing an independent in-result version field.
- **FR-023**: System MUST require a manual full re-run and full historical re-backfill of all datasets whenever a library release changes trend-analysis behavior, to preserve cross-series consistency.
- **FR-024**: System MUST fail fast with an explicit error when cadence cannot be inferred confidently from observation spacing, using the same dataset-scoped trend-processing failure model as seasonality-classification change handling.
- **FR-025**: System MUST produce exactly deterministic analysis outputs for identical input series under the same library version, including label, direction, seasonality flags, and supporting metrics.
- **FR-026**: System MUST implement trend processing as a dedicated Dagster asset that is downstream from the data fetch/update asset path, rather than embedding trend execution inside core observation write loops.
- **FR-027**: System MUST trigger trend processing from the output of completed dataset fetch/update work so that trend analysis operates on persisted post-update series state.
- **FR-028**: System MUST treat a trend-asset failure as a source-branch-scoped failure that marks only the affected source branch/asset chain failed, while allowing other independent source branches/assets in the same run to continue.
- **FR-029**: System MUST enforce state-based idempotency for trend lifecycle persistence so retries over identical persisted observation state do not create additional lifecycle records.
- **FR-030**: System MUST execute the downstream trend asset per updated series based on upstream-emitted series updates, rather than batching all series into a single trend-processing unit.
- **FR-031**: System MUST mark downstream trend-asset execution successful for insufficient_data and no_significant_trend outcomes, emit explicit no-op outcome metadata, and avoid trend lifecycle writes when the outcome requires no lifecycle transition.
- **FR-032**: System MUST support touch interaction for trend spans where a single tap opens a pinned trend tooltip and tapping elsewhere dismisses it.
- **FR-033**: System MUST render trend visualization spans as non-overlapping regions; any overlapping intervals in incoming trend span payloads MUST be normalized before rendering.

### Assumptions and Dependencies

- Trend detection outcomes from the validated spike logic are suitable as the baseline behavior for productionization.
- Trend detection capability will be delivered as a reusable shared processing component consumed by ingestion runtime.
- Analysis behavior changes are governed by library release versioning and require explicit operator-triggered global recomputation.
- Existing dataset identifiers and observation time series remain the source of truth for trend evaluation scope.
- Recent updates feed supports heterogeneous event types as long as ordering semantics are preserved.

### Key Entities _(include if feature involves data)_

- **Trend Record**: A persisted segment describing one detected trend period for a dataset, including direction, significance classification, seasonality classification, start period, optional end period, and ongoing flag.
- **Trend Signature**: The persisted comparison key for continuity decisions, consisting of top-level trend label plus direction, strength, and seasonality classification dimensions.
- **Trend Transition Event**: A lifecycle event representing creation, closure, or continuation decision for trend records when new observations are processed.
- **Trend Feed Item**: A recent-updates item type representing a newly identified trend or trend state change, normalized with dataset update items for shared ordering.
- **Trend Visualization Span**: A dataset detail chart annotation object describing start/end coordinates, direction color semantics, and hover detail payload.
- **Trend Analysis Result**: A pure output object returned by the library containing classification label, confidence/significance metadata, seasonality metadata, and terminal statuses such as insufficient_data for caller-side handling.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of seasonality-classification changes for ongoing trends produce dataset-scoped trend-processing failures with explicit error reasons while core observation ingestion remains successful.
- **SC-002**: For a validation set of known trend transitions, at least 95% of transitions produce exactly one closed historical trend segment and one new ongoing segment when a change occurs.
- **SC-003**: In recent updates responses containing trend activity, users can identify trend events and dataset updates in one ordered feed with no missing trend events.
- **SC-004**: In dataset detail views with trend data, users can identify direction and time span of active and historical trends from chart highlights within 10 seconds in usability verification.
- **SC-005**: When no trend exists for a dataset, dataset detail and recent updates remain fully usable with no regression in baseline interactions.
- **SC-006**: Repeated executions of the trend library on identical input data under the same library version produce byte-equivalent result payloads in 100% of verification runs.

## Constitution Alignment _(mandatory)_

<!--
  ACTION REQUIRED: Confirm this feature complies with repository constitution rules.
  Any item marked "No" requires explicit owner-approved exception before implementation.
-->

- **CA-001 Quality Gates**: Yes
- **CA-002 Coverage**: Yes
- **CA-003 Local Stack**: Yes
- **CA-004 Contracts and Data Integrity**: Yes
- **CA-005 Documentation Fidelity**: Yes
- **CA-006 Configuration Integrity**: N/A
- **CA-007 Frontend UI System**: Yes
