# Feature Specification: Gap-Tolerant Cadence Inference

**Feature Branch**: `[047-handle-cadence-gaps]`  
**Created**: 2026-04-05  
**Status**: Draft  
**Input**: User description: "What I would like to do in this case is just add some better handling for gaps in the daylight like this it's really true irregular data because all of the data after this Gap is perfectly regular it's just a gap and it should be treated as such. please create a spec for that work"

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

### User Story 1 - Continue Processing Through Isolated Gaps (Priority: P1)

As a pipeline operator, I need trend processing to treat a one-off historical gap as a data gap rather than true irregular cadence so ingestion can continue for otherwise regular series.

**Why this priority**: This directly addresses the current production-blocking failure mode where a single historical gap causes source-level trend processing failures.

**Independent Test**: Can be fully tested by running ingestion for a known weekly or monthly series containing one isolated large gap and confirming trend processing completes without an irregular-spacing failure.

**Acceptance Scenarios**:

1. **Given** a series where nearly all adjacent observations match one cadence and one historical long gap exists, **When** trend processing evaluates cadence, **Then** the series is treated as regular with a recognized gap and trend processing continues.
2. **Given** a source run that includes at least one gap-affected but otherwise regular series, **When** the run completes, **Then** the source outcome is not marked failed due to irregular-spacing cadence error for that series.

---

### User Story 2 - Preserve True Irregular Detection (Priority: P2)

As a data-quality owner, I need truly irregular series to keep failing cadence checks so the system does not silently accept data that cannot support trustworthy trend classification.

**Why this priority**: Gap tolerance must not weaken existing guardrails against genuinely irregular interval patterns.

**Independent Test**: Can be tested by replaying a series with recurring mixed interval patterns and confirming cadence still resolves as irregular with explicit failure outcomes.

**Acceptance Scenarios**:

1. **Given** a series with recurring mixed interval behavior that cannot be explained by isolated gaps, **When** cadence is evaluated, **Then** trend processing fails with explicit irregular-spacing outcome.
2. **Given** a series with insufficient points or non-increasing observation dates, **When** cadence is evaluated, **Then** existing invalid-cadence failure behavior is preserved.

---

### User Story 3 - Explain Gap-Tolerant Decisions (Priority: P3)

As an operator investigating run outcomes, I need clear decision metadata when gap tolerance is applied so I can distinguish accepted gap handling from true irregularity failures.

**Why this priority**: Operational confidence depends on transparent run reasoning, especially when cadence handling changes from fail-fast to tolerate-isolated-gap behavior.

**Independent Test**: Can be tested by running the same series twice and validating that decision metadata consistently indicates whether gap tolerance was applied and why.

**Acceptance Scenarios**:

1. **Given** a series accepted via gap-tolerant cadence handling, **When** run outcomes are reviewed, **Then** outcome metadata records that a gap-tolerant decision was used.
2. **Given** identical input observations across repeated runs, **When** cadence is re-evaluated, **Then** the same cadence decision and gap-tolerance rationale are produced.

---

### Edge Cases

- What happens when a series has one early historical gap followed by decades of regular weekly or monthly spacing?
- What happens when a series has multiple large gaps spread across the timeline instead of one isolated gap?
- What happens when a series alternates between two cadence patterns across long periods (for example, repeated weekly then monthly blocks)?
- What happens when the latest section of the series contains the long gap rather than only early history?
- What happens when a series has duplicate or out-of-order observation dates in addition to a gap?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST evaluate observation spacing in a way that distinguishes isolated historical gaps from persistent irregular spacing.
- **FR-002**: System MUST treat a series as cadence-valid when the non-gap majority of intervals align to a single supported cadence and any off-cadence intervals satisfy isolated-gap policy.
- **FR-003**: System MUST continue trend evaluation and persistence for cadence-valid series that include isolated gaps.
- **FR-004**: System MUST preserve explicit failure outcomes for series that remain cadence-invalid after isolated-gap policy is applied.
- **FR-005**: System MUST preserve explicit failure outcomes for non-increasing observation order and insufficient-history cadence conditions.
- **FR-006**: System MUST apply the same cadence decision rules during first-run backfill and incremental processing.
- **FR-007**: System MUST produce deterministic cadence decisions for identical observation input sequences across repeated runs.
- **FR-008**: System MUST include explicit outcome metadata indicating whether cadence was accepted through standard regularity or isolated-gap tolerance.
- **FR-009**: System MUST include enough outcome context for operators to identify which series and observation range triggered a cadence-invalid failure.
- **FR-010**: System MUST ensure source-level outcomes do not report cadence irregularity failures for series that qualify as isolated-gap cadence-valid.
- **FR-011**: System MUST keep true irregular-spacing guardrails in place so mixed-cadence datasets are still rejected.
- **FR-012**: System MUST include automated coverage for isolated-gap acceptance, true-irregular rejection, and deterministic rerun behavior.

### Assumptions and Dependencies

- Supported cadence families remain daily, weekly, and monthly.
- This feature focuses on cadence evaluation behavior in trend processing and does not require new user-facing UI changes.
- Existing ingestion data contracts and source ownership behavior remain unchanged.
- Existing run outcome surfaces are available for exposing cadence decision context.
- Local compose-driven pipeline execution remains the validation environment for acceptance testing.

### Key Entities _(include if feature involves data)_

- **Observation Spacing Profile**: The ordered list of adjacent observation intervals for a series, used to determine whether cadence is regular, gap-tolerant, or irregular.
- **Cadence Decision Outcome**: The decision result for one series in one processing pass, including cadence validity state and reason metadata.
- **Gap Event Context**: A bounded interval anomaly that is treated as a recognized data gap when it meets isolated-gap policy.
- **Source Trend Outcome**: The source-level processing status that aggregates per-series cadence decisions and trend-processing results.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of validation series with one isolated historical gap and otherwise regular spacing complete trend processing without cadence-irregularity failure.
- **SC-002**: 100% of validation series with persistent mixed spacing continue to be rejected as cadence-irregular.
- **SC-003**: In controlled reruns of known affected sources, cadence-related source failures for isolated-gap series are reduced from current baseline to zero.
- **SC-004**: 100% of audited cadence decisions in run outcomes include a clear reason state indicating regular cadence, isolated-gap tolerance, or true irregular rejection.
- **SC-005**: 100% of deterministic rerun checks on unchanged input produce the same cadence decision classification.

## Scope Boundaries

- In scope: cadence decision behavior for gaps vs true irregular spacing in trend processing and related run outcomes.
- Out of scope: redesign of trend scoring semantics, new cadence families, and frontend visual changes.

## Future Data Risk Note

- The isolated-gap tolerance policy in this feature is calibrated to the currently observed data suite.
- If future datasets contain materially higher or structurally different irregular spacing patterns, this policy may no longer be sufficient.
- In that case, cadence handling SHOULD be re-evaluated and revised, rather than assuming the current threshold and rules remain universally valid.

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
  (N/A)
