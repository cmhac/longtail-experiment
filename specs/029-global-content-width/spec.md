# Feature Specification: Global Page Content Width

**Feature Branch**: `[029-global-content-width]`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Build a global max width applied to multiple pages so home and datasets content do not span the entire screen on very large desktop displays, while still allowing explicit full-width layouts when needed."

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

### User Story 1 - Read Comfortable Layouts on Large Screens (Priority: P1)

As a desktop visitor, I can read page content within a constrained content width on wide displays so text and dataset rows remain comfortable to scan.

**Why this priority**: Readability and scannability on common large desktop monitors is the primary business need for this change.

**Independent Test**: Open home and datasets pages on a wide desktop viewport and verify the main page content is centered and constrained instead of spanning edge-to-edge.

**Acceptance Scenarios**:

1. **Given** the application is viewed on a large desktop display, **When** a shell page loads, **Then** primary page content is presented within a consistent maximum readable width.
2. **Given** the home page recent updates section is visible, **When** rows render on a wide display, **Then** entries remain within the same constrained content region as surrounding page content.
3. **Given** the datasets listing page is visible, **When** listing rows render on a wide display, **Then** the list remains constrained to the shared page content width.

---

### User Story 2 - Preserve Intentional Full-Width Surfaces (Priority: P2)

As a product designer, I can explicitly mark selected surfaces as full-width so intentional edge-to-edge regions continue to render correctly.

**Why this priority**: A global default should not break existing shell regions that are intentionally full-width.

**Independent Test**: Verify that designated full-width surfaces still render edge-to-edge while default page content remains constrained.

**Acceptance Scenarios**:

1. **Given** a page surface is explicitly designated as full-width, **When** the page renders, **Then** that surface spans the full available width.
2. **Given** a page surface is not explicitly designated as full-width, **When** the page renders, **Then** it inherits the global max-width behavior.

---

### User Story 3 - Keep Layout Behavior Consistent Across Pages (Priority: P3)

As a maintainer, I can rely on one shared default width policy for shell pages so new and existing pages behave consistently without repeated one-off layout decisions.

**Why this priority**: Consistency reduces maintenance cost and prevents visual drift as additional pages are added.

**Independent Test**: Compare multiple shell pages and confirm they follow one shared default width policy unless an explicit full-width exception is declared.

**Acceptance Scenarios**:

1. **Given** multiple shell pages exist, **When** they render at desktop sizes, **Then** their default content regions align to the same max-width rule.
2. **Given** future pages are added to the shell, **When** they do not request full-width layout, **Then** they automatically use the same constrained content width behavior.

---

### Edge Cases

- What happens on ultra-wide desktop displays where available width greatly exceeds readable line length? Default page content should remain centered and constrained without stretching.
- What happens when a page mixes constrained sections with intentionally full-width sections? Each section should follow its declared layout mode without affecting neighboring sections.
- What happens when long titles, summaries, or tag lists appear inside constrained layouts? Content should wrap and remain readable without clipping or overlap.
- What happens on narrow viewports where a max width would be smaller than the viewport? Content should continue to fill available width naturally on smaller screens.
- What happens for legacy pages that were previously full-width by default? They should receive constrained default behavior unless explicitly marked as full-width exceptions.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST define one global default maximum content width policy for shell page content regions.
- **FR-002**: The system MUST apply the global default width policy to primary content regions on all shell pages unless an explicit override is declared.
- **FR-003**: The system MUST keep default-constrained content centered horizontally within the viewport at desktop sizes.
- **FR-004**: The system MUST preserve existing page hierarchy and behavior while changing width behavior (navigation, filters, sorting, and fallback states remain functionally unchanged).
- **FR-005**: The system MUST allow explicit full-width opt-out behavior for surfaces that are intentionally designed to span edge-to-edge.
- **FR-006**: The system MUST ensure full-width opt-out behavior is explicit and predictable, not inferred from incidental styling.
- **FR-007**: The system MUST maintain readable presentation for dataset rows and supporting text when constrained by the global width policy.
- **FR-008**: The system MUST preserve responsive behavior so constrained content still uses available width on smaller viewports.
- **FR-009**: The system MUST apply the same default width behavior to both home and datasets list pages as part of this feature.
- **FR-010**: The system MUST define validation coverage that confirms default-constrained behavior and explicit full-width exceptions across representative shell pages.

### Key Entities _(include if feature involves data)_

- **Global Content Width Policy**: Shared rule that governs maximum width and centering behavior for default shell page content.
- **Page Layout Region**: A renderable page surface that can inherit default constrained width or request explicit full-width behavior.
- **Full-Width Exception**: Explicit designation that allows a specific region to bypass default max-width constraints.
- **Layout Validation Scenario**: Testable page/view combinations used to verify consistent width behavior across routes and viewport sizes.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In layout QA on wide desktop viewports, 100% of sampled default shell page content regions render with constrained readable width instead of edge-to-edge span.
- **SC-002**: In route parity checks, 100% of sampled home and datasets list page content regions follow the same default width behavior.
- **SC-003**: In exception checks, 100% of explicitly designated full-width regions continue to render edge-to-edge while adjacent default content remains constrained.
- **SC-004**: In responsive checks across desktop and mobile breakpoints, 100% of sampled pages retain readable, non-overlapping content after global width constraints are applied.

## Constitution Alignment _(mandatory)_

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

## Assumptions

- The feature applies to user-facing pages built on the shared shell layout.
- Header and footer regions that are intentionally full-width remain full-width unless separately changed.
- A single shared default max-width policy is preferable to page-by-page width tuning for this phase.
- No backend or data contract changes are required for this layout-only scope.

## Dependencies

- Existing shared shell page structure and route composition.
- Existing page-level visual regression and structural tests that can be extended for width behavior.
- Existing design direction that allows explicit full-width regions where required.
