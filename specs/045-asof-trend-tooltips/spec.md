# Feature Specification: Historical As-Of Trend Tooltips

**Feature Branch**: `[045-asof-trend-tooltips]`  
**Created**: 2026-04-02  
**Status**: Draft  
**Input**: User description: "Create a new spec for wiring historical as-of trend by observation into backend API and frontend, then show a trend indicator chip in each dataset-detail historical trend tooltip."

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

### User Story 1 - Retrieve Historical As-Of Trend State (Priority: P1)

As a dataset consumer, I need each observation point to resolve the trend state that was true at that same observation time so chart interactions can answer "what was the trend then" instead of only "what is the trend now".

**Why this priority**: This is the core data behavior. Without reliable as-of trend retrieval, tooltip history cannot be trusted.

**Independent Test**: Can be fully tested by requesting one dataset detail payload with multiple observations and verifying trend state can be resolved for each observation timestamp where trend state exists.

**Acceptance Scenarios**:

1. **Given** a dataset has historical observations and persisted trend history, **When** detail data is requested, **Then** trend state can be resolved for each observation based on that observation's recorded time.
2. **Given** an observation has no available trend state, **When** detail data is requested, **Then** the observation still returns successfully with an explicit no-trend outcome for tooltip rendering.
3. **Given** repeated requests for the same dataset and observation range, **When** detail data is requested multiple times, **Then** as-of trend resolution remains deterministic for matching inputs.

---

### User Story 2 - Expose As-Of Trend Data In Detail Contract (Priority: P2)

As an application consumer, I need dataset detail responses to include per-observation as-of trend information so the frontend can render historical trend context without separate lookup calls.

**Why this priority**: Contract delivery is required before UI can display as-of trend context in tooltips.

**Independent Test**: Can be tested by validating detail response shape includes observation-level as-of trend payloads and preserves existing detail behavior when trend data is partially absent.

**Acceptance Scenarios**:

1. **Given** dataset detail is requested, **When** the response is returned, **Then** each observation item includes resolved as-of trend information or explicit unavailable state.
2. **Given** the dataset has mixed availability across observation history, **When** detail data is requested, **Then** available and unavailable as-of trend states are both represented in a structurally valid payload.
3. **Given** a detail response contains malformed or inconsistent as-of trend data, **When** response validation runs, **Then** the request fails with explicit contract error semantics.

---

### User Story 3 - Show As-Of Trend Chip In Historical Tooltip (Priority: P3)

As an end user, I need the chart tooltip for each observation to show the trend indicator chip for that specific observation so I can quickly understand what trend was active at that time.

**Why this priority**: Tooltip presentation is the visible product value and depends on the data and contract work from P1 and P2.

**Independent Test**: Can be tested by opening a dataset detail chart, interacting with multiple observations, and verifying each tooltip shows the observation-specific trend chip at the bottom of the tooltip.

**Acceptance Scenarios**:

1. **Given** an observation with available as-of trend data, **When** its chart tooltip opens, **Then** the tooltip shows the directional trend chip at the bottom.
2. **Given** an observation without available as-of trend data, **When** its chart tooltip opens, **Then** the tooltip shows the explicit unavailable chip state at the bottom.
3. **Given** users inspect different points in the same chart, **When** tooltips change between observations, **Then** the chip updates to each observation's resolved as-of trend state.

---

### Edge Cases

- What happens when multiple observations share the same recorded date but have different report timestamps?
- What happens when trend history exists for newer observations but not for older observations in the requested chart window?
- What happens when an observation is present in detail payload but its as-of trend linkage is missing or orphaned?
- What happens when observation date filters return sparse ranges where only some points have trend state?
- What happens when the tooltip is opened on very dense chart points where users move quickly across observations?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST support resolving trend state for an observation by using that observation's recorded time context.
- **FR-002**: System MUST include observation-level as-of trend payloads in dataset detail responses used by historical chart tooltips.
- **FR-003**: System MUST preserve existing latest canonical trend fields in detail responses while adding observation-level as-of trend fields.
- **FR-004**: System MUST return an explicit unavailable as-of trend state when no trend is available for a specific observation.
- **FR-005**: System MUST keep observation ordering stable while adding as-of trend payload fields.
- **FR-006**: System MUST apply deterministic as-of trend selection rules when multiple trend candidates could map to the same observation.
- **FR-007**: System MUST validate observation-level as-of trend payload shape before returning dataset detail responses.
- **FR-008**: System MUST fail with explicit contract errors when as-of trend payloads are malformed.
- **FR-009**: System MUST display one trend indicator chip in the chart tooltip for each observation interaction on dataset detail pages.
- **FR-010**: System MUST place the trend chip at the bottom section of each observation tooltip.
- **FR-011**: System MUST render the chip using the resolved as-of trend state for that observation, not the latest dataset-level trend state.
- **FR-012**: System MUST render an unavailable chip state in the tooltip when observation-level trend state is unavailable.
- **FR-013**: System MUST keep non-tooltip dataset detail chart behavior unchanged.
- **FR-014**: System MUST maintain compatibility for datasets without historical trend rows by continuing to render chart tooltips safely.
- **FR-015**: System MUST include automated coverage for observation-level trend retrieval, detail response validation, and tooltip chip rendering behavior.

### Key Entities _(include if feature involves data)_

- **Observation As-Of Trend State**: The trend state associated with one specific observation timestamp, including available/unavailable status and indicator semantics.
- **Observation Tooltip Trend View Model**: The tooltip-ready projection of one observation plus its resolved as-of trend chip data.
- **Dataset Detail Observation Trend Envelope**: The response-level structure that carries observation points and per-observation as-of trend state together.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of audited dataset-detail responses include observation-level as-of trend fields for returned observations.
- **SC-002**: 100% of observations with available persisted trend history resolve to the correct as-of trend state in validation datasets.
- **SC-003**: 100% of tooltip regression checks show exactly one trend chip at the bottom of the tooltip for each tested observation interaction.
- **SC-004**: In mixed-availability datasets, 100% of observations without resolved trend state show the explicit unavailable chip state instead of empty or broken tooltip regions.
- **SC-005**: At least 95% of users in usability validation can identify the historical trend state for a hovered observation within 5 seconds.

## Assumptions

- Persisted trend history already contains enough observation-linked records to resolve at least a subset of historical observations.
- Dataset detail remains the only surface in scope for per-observation historical trend tooltip chips in this feature.
- Existing chart tooltip interaction patterns remain unchanged except for adding the chip content at the bottom.
- Trend state semantics for chip rendering reuse existing indicator state definitions.

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
