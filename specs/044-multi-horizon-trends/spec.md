# Feature Specification: Current-State Multi-Lookback Trends

**Feature Branch**: `[044-multi-horizon-trends]`  
**Created**: 2026-04-01  
**Status**: Draft  
**Input**: User description: "Classify current trend state across fixed observation lookbacks. Run all applicable lookbacks in parallel per new observation, gate by dataset frequency and history depth, and replace the removed detail-page trend chip with a directional arrow indicator. Show that same indicator at the right edge of all dataset list rows, and ensure dataset-list and dataset-detail responses both include the current trend needed for direct rendering."

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

### User Story 1 - Persist Observation-Level Lookback Snapshots (Priority: P1)

As a platform operator, I need each new observation to produce independent trend classifications for all applicable observation lookbacks so we store current trend state by lookback depth rather than by date-bucket periods.

**Why this priority**: This is the core model shift. Without per-observation multi-lookback snapshots, downstream consumers cannot reliably answer "what is the trend right now" across short and long lookback depths.

**Independent Test**: Can be fully tested by materializing one new observation for a dataset and verifying that lookback-specific current-trend snapshots are written only for applicable lookbacks.

**Acceptance Scenarios**:

1. **Given** a dataset receives a new observation, **When** trend processing runs, **Then** the system classifies and stores current-trend snapshots for all applicable lookbacks in parallel.
2. **Given** a dataset does not satisfy frequency or history requirements for some lookbacks, **When** trend processing runs, **Then** inapplicable lookbacks are skipped with explicit applicability outcomes and applicable lookbacks still persist.
3. **Given** a lookback produces no actionable trend signal for the current observation, **When** processing runs, **Then** the stored snapshot explicitly records a no-significant-trend current state for that lookback.

---

### User Story 2 - Serve Current Trend Across List and Detail Responses (Priority: P2)

As an application consumer, I need current trend data in both dataset-list and dataset-detail responses so clients can show the current trend consistently wherever a dataset appears.

**Why this priority**: Parallel snapshot persistence only creates value when response payloads expose both summary-level current trend state for list surfaces and detailed lookback context for detail surfaces.

**Independent Test**: Can be tested by requesting dataset list and dataset detail payloads and validating that each dataset includes deterministic current trend state for direct rendering, plus lookback snapshot detail where required.

**Acceptance Scenarios**:

1. **Given** a dataset appears in any dataset-list response, **When** that response is requested, **Then** the response includes one canonical current trend descriptor for that dataset suitable for direct list-row rendering.
2. **Given** a dataset detail page is requested, **When** detail data is returned, **Then** the response includes the canonical current trend descriptor and lookback snapshots in deterministic structures.
3. **Given** some lookbacks are not applicable for a dataset, **When** detail data is requested, **Then** the response includes explicit lookback availability state instead of failing the request.
4. **Given** no applicable or available current trend exists for a dataset, **When** list or detail data is requested, **Then** the response includes an explicit unavailable current-trend state instead of omitting the field.
5. **Given** a client requests unsupported lookback identifiers, **When** the request is processed, **Then** the system returns explicit validation errors.

---

### User Story 3 - Show a Single Informative Trend Indicator (Priority: P3)

As an end user, I want a simple arrow-based trend indicator that appears at the right edge of dataset rows and beside the Historical Trend heading so I can quickly understand the current trend without reading a chip label or parsing chart overlays.

**Why this priority**: The current overlay approach is being intentionally removed for simplicity and clarity, and trend signaling must remain compact and consistent across discovery surfaces.

**Independent Test**: Can be tested by opening list and detail pages and verifying the overlay no longer appears, the directional indicator renders in the expected positions, and the same current-trend state is represented consistently across surfaces.

**Acceptance Scenarios**:

1. **Given** a dataset list row renders for a dataset with an available canonical trend descriptor, **When** the row is displayed, **Then** one directional arrow indicator appears at the far right of that row.
2. **Given** a dataset detail page loads for a dataset with an available canonical trend descriptor, **When** the page is displayed, **Then** the same directional arrow indicator appears adjacent to the Historical Trend heading above the chart.
3. **Given** canonical trend descriptor data is provided by the API, **When** list or detail pages render, **Then** the indicator renders that descriptor without performing client-side trend weighting or lookback ranking logic.
4. **Given** the canonical descriptor represents a strong uptrend, mild uptrend, mild downtrend, or strong downtrend, **When** the indicator renders, **Then** the arrow orientation and color match the corresponding state consistently.
5. **Given** trend overlay visualization existed previously, **When** the updated detail page loads, **Then** no trend overlay is rendered.
6. **Given** no applicable or available current trend exists, **When** a list row or detail page renders, **Then** the indicator area communicates unavailable trend status clearly.

---

### Edge Cases

- What happens when a dataset has enough history for short lookbacks but not for deep lookbacks (for example 250, 500, or 1000)?
- What happens when low-update datasets make short lookbacks less informative while deep lookbacks remain applicable?
- What happens when one or more lookbacks fail during processing while others succeed for the same observation?
- What happens when a dataset’s update behavior changes over time and lookback applicability changes?
- What happens when clients request unsupported or duplicate lookback identifiers?
- What happens when no lookback is applicable, leaving list and detail indicator placements without a trend to display?
- What happens when a dataset list mixes datasets with available and unavailable current-trend states in the same response?
- What happens when a canonical descriptor direction is available but strength is missing or unsupported for arrow-state mapping?
- What happens when row density or narrow viewports reduce the space available for the right-aligned list indicator?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST support the following fixed observation-lookback catalog for current trend classification: 1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500, and 1000 observations ago.
- **FR-002**: System MUST evaluate lookback applicability per series using both update frequency characteristics and historical observation availability before running classification.
- **FR-003**: System MUST only run a lookback when the series has enough observations to satisfy that lookback depth.
- **FR-004**: System MUST enforce centrally defined applicability rules so lookbacks run only when frequency and depth requirements are satisfied.
- **FR-005**: System MUST execute classification independently in parallel across all applicable lookbacks for each new observation.
- **FR-006**: System MUST persist one current-state trend snapshot per applicable lookback tied to the specific observation and observation date.
- **FR-007**: System MUST persist explicit inapplicability outcomes for lookbacks that are not applicable for a given series/observation context.
- **FR-008**: System MUST persist explicit no-significant-trend outcomes when a lookback is applicable but does not produce an actionable trend signal.
- **FR-009**: System MUST treat unchanged observation reprocessing as idempotent and avoid duplicate lookback snapshots for the same observation.
- **FR-010**: System MUST isolate failures so an error in one lookback does not block successful snapshot persistence for other applicable lookbacks.
- **FR-011**: System MUST expose current trend snapshots by lookback in dataset/trend responses, including lookback availability and applicability state.
- **FR-012**: System MUST return explicit validation errors for unsupported lookback identifiers in client requests.
- **FR-013**: System MUST compute a deterministic weighted heuristic across applicable lookbacks to produce one canonical current trend descriptor per observation context.
- **FR-014**: System MUST remove the dataset-detail trend overlay visualization and its related response dependencies.
- **FR-015**: System MUST persist the canonical weighted-heuristic trend descriptor in backend storage so it is available without client recomputation.
- **FR-016**: System MUST expose the canonical weighted-heuristic trend descriptor in dataset-detail API responses for direct client rendering.
- **FR-017**: System MUST expose the canonical weighted-heuristic trend descriptor in every dataset-list API response that returns dataset summary rows, so list surfaces can render the current trend without additional trend-specific fetches.
- **FR-018**: System MUST render one directional current-trend indicator at the far right of each dataset row using the API-provided canonical descriptor.
- **FR-019**: System MUST render the same directional current-trend indicator adjacent to the Historical Trend heading on dataset detail pages using the API-provided canonical descriptor.
- **FR-020**: System MUST map canonical current-trend states to four visual indicator states: straight-up green for strong uptrend, up-right green for mild uptrend, down-right red for mild downtrend, and straight-down red for strong downtrend.
- **FR-021**: System MUST render a clear unavailable state for list and detail indicators when no applicable or available current trend snapshot exists.
- **FR-022**: System MUST preserve auditability by recording lookback attribution and decision status for each per-observation trend evaluation.
- **FR-023**: System MUST support controlled reclassification workflows that recompute current-state lookback snapshots and canonical weighted descriptors across historical observations when needed.
- **FR-024**: System MUST deprecate reliance on canonical trend start/end period records for primary product behavior in this feature scope.
- **FR-025**: System MUST produce deterministic lookback snapshot outputs and canonical weighted descriptors for identical observation inputs, frequency interpretation, and lookback applicability configuration.

### Key Entities _(include if feature involves data)_

- **Observation Lookback**: A fixed lookback depth (N observations ago) evaluated independently.
- **Lookback Applicability Result**: A per-series, per-lookback decision indicating applicable, inapplicable, and reason context based on update behavior and depth.
- **Observation Lookback Snapshot**: A per-observation, per-lookback current trend result including trend state and evaluation timestamp.
- **Observation Lookback Evaluation Outcome**: A per-run result for each lookback (applied, inapplicable, no-significant-trend, error) with traceable reason context.
- **Canonical Trend Descriptor**: A weighted-heuristic aggregate derived from applicable lookback snapshots, persisted for API delivery and direct client rendering.
- **Dataset Trend Indicator Model**: A client-facing projection of the API-provided canonical trend descriptor for row-level and detail-heading recent trend display.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of newly ingested observations for applicable datasets produce current-state snapshots for all lookbacks that pass applicability rules.
- **SC-002**: 100% of inapplicable lookbacks produce explicit inapplicability outcomes with reason attribution rather than silent omission.
- **SC-003**: 100% of audited dataset-detail responses and dataset-list responses provide structurally valid canonical current-trend descriptor payloads for direct rendering.
- **SC-004**: Dataset detail pages show no trend overlay visualization and show exactly one directional trend indicator (or explicit unavailable state) adjacent to the Historical Trend heading in 100% of UI regression checks.
- **SC-005**: Reprocessing unchanged observations results in zero duplicate per-observation lookback snapshots in 100% of idempotency verification cases.
- **SC-006**: In simulated partial-failure runs, unaffected applicable lookbacks still persist successfully for the same observation in 100% of test cases.
- **SC-007**: 100% of audited dataset-row and dataset-detail indicator renders use API-provided canonical descriptors with no client-side lookback weighting or ranking execution.
- **SC-008**: 100% of visual-regression checks for the four supported current-trend states render the correct arrow orientation and red/green direction encoding across dataset-list and dataset-detail surfaces.

## Assumptions

- The fixed lookback catalog in this feature is limited to 1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500, and 1000 observations ago.
- Applicability rules will be centrally defined and versioned so frequency/depth gating is deterministic across pipeline and API behavior.
- Current-state per-observation snapshots are the primary trend product output for this feature; historical canonical start/end segmentation is not.
- Weighted-heuristic canonical descriptor computation occurs upstream and is persisted; clients consume the resulting descriptor and do not reproduce weighting logic.
- The dataset-detail UI in this feature scope only needs one primary trend indicator adjacent to the Historical Trend heading, derived from the API-provided canonical descriptor.
- Dataset-list surfaces in scope reuse shared dataset-row behavior and each require the same API-provided current-trend indicator state without extra per-row requests.
- Specific statistical or machine-learning classification methods are intentionally out of scope for this specification revision.

## Constitution Alignment _(mandatory)_

<!--
  ACTION REQUIRED: Confirm this feature complies with repository constitution rules.
  Any item marked "No" requires explicit owner-approved exception before implementation.
-->

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code, and the
  full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before
  commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects, and can satisfy the commit-time coverage stop rule
  (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
- **CA-006 Configuration Integrity**: Any new service or pipeline component that requires
  credentials or external API keys will fail hard (exception/non-zero exit/job-level
  failure) when those variables are absent — no soft outcome recording, no silent
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source
  for any Docker Compose service that requires secrets. (N/A)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI
  components, Tailwind utilities, and shared abstractions in
  `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate
  one-off component patterns or new local CSS without a documented exception.
  (Yes)
