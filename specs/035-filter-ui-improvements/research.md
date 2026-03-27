# Phase 0 Research: Filter UI Improvements

## Decision 1: Align filter container background with existing shared surface tokens

- Decision: Use the same shared shell/filter surface styling semantics already used by discovery container surfaces for the dataset-list filter control box.
- Rationale: Reusing established surface tokens keeps visual language consistent across pages and appearance modes while minimizing drift.
- Alternatives considered:
  - Hard-code a new standalone filter background color: rejected due to long-term inconsistency risk.
  - Keep current mixed styling: rejected because it fails the visual consistency goal in the specification.

## Decision 2: Replace existing dropdown controls with combo-box style controls while preserving filter semantics

- Decision: Migrate the three dataset-list selector controls to combo-box style interactions without changing existing filter/sort meaning, selected value mapping, or query behavior.
- Rationale: Improves discoverability and interaction quality while preserving existing user expectations and backend request semantics.
- Alternatives considered:
  - Partial migration (only filter selectors, not sort): rejected because the scope calls for replacing the dropdown controls in that component.
  - Preserve native dropdowns and only restyle: rejected because modernization of control interaction is an explicit requirement.

## Decision 3: Adopt left-group/right-group control layout with capped widths

- Decision: Present two filtering controls as a left-aligned group and the sort control as a separate right-aligned group, with a deliberate gap between groups and capped control widths.
- Rationale: Establishes clear information hierarchy and avoids full-row stretched controls, matching the requested visual pattern.
- Alternatives considered:
  - Keep all controls evenly distributed in one continuous group: rejected because it does not reflect the requested separation of filters and sort.
  - Allow controls to expand to full available width: rejected because the requested target uses capped widths.

## Decision 4: Preserve keyboard and responsive usability as non-negotiable invariants

- Decision: Require keyboard-operable selector behavior and responsive layout reflow that keeps grouping intent understandable.
- Rationale: Layout and control changes must not regress accessibility or usability on smaller viewports.
- Alternatives considered:
  - Treat keyboard behavior as out-of-scope for this UI pass: rejected because control replacement can regress accessibility if not explicitly protected.
  - Maintain desktop-only layout guarantees: rejected because spec scope includes desktop and mobile readability/usability.

## Decision 5: Validate via focused frontend regression tests plus mandatory monorepo stop gates

- Decision: Add/adjust frontend tests for control rendering and behavior continuity, then run mandatory full-suite monorepo tests and coverage checks.
- Rationale: This feature is visual and interaction heavy; targeted checks catch local regressions while stop gates enforce repository policy.
- Alternatives considered:
  - Manual checks only: rejected because repository constitution requires automated quality coverage.
  - Stop at targeted tests only: rejected because mandatory full-suite and coverage stop rules apply before completion/commit.
