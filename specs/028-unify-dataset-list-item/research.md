# Research: Unified Dataset List Item

## Decision 1: Use homepage editorial row as the shared baseline

- Decision: Treat the current homepage recent-updates row visual hierarchy as the canonical row pattern for both home and datasets list surfaces.
- Rationale: The user-directed requirement explicitly selects the homepage design as source of truth and this pattern already communicates dataset metadata in an editorial scan-first layout.
- Alternatives considered:
  - Keep datasets page card styling and only tweak typography: rejected because it preserves dual implementations and visual divergence.
  - Create a third new visual treatment for both pages: rejected because it introduces unnecessary redesign risk versus the selected baseline.

## Decision 2: Preserve page-level interaction semantics while sharing row rendering

- Decision: Share row presentation logic while keeping each page’s surrounding behavior unchanged (home feed fallback flow and datasets filter/sort interactions).
- Rationale: The feature goal is UI consistency for row items, not workflow redesign for either page.
- Alternatives considered:
  - Force identical click behavior on both pages (row-wide links everywhere): rejected as scope expansion and potential behavior regression for datasets list usage patterns.
  - Keep separate row components with copied markup: rejected due to duplication risk and future drift.

## Decision 3: Keep datasets control strip styling out of scope

- Decision: Exclude source/category/sort dropdown restyling from this feature.
- Rationale: User explicitly approved current dropdown styling difference for now.
- Alternatives considered:
  - Restyle controls to match homepage row aesthetics in this feature: rejected as additional scope with no direct requirement.

## Decision 4: Normalize metadata rendering contract between contexts

- Decision: Shared row contract includes source attribution, date label, title, summary, and pills; optional metadata should degrade gracefully in both contexts.
- Rationale: Consistency target requires the same core content hierarchy wherever dataset rows appear.
- Alternatives considered:
  - Context-specific metadata fields with optional divergence: rejected because it weakens consistency and complicates testing.

## Decision 5: Validate unification with regression-focused tests

- Decision: Maintain/expand tests for both pages to verify shared row hierarchy and unchanged page-specific behavior.
- Rationale: Reusing one component across two surfaces increases regression blast radius unless both pathways are validated together.
- Alternatives considered:
  - Snapshot-only coverage of the shared component: rejected because page-level integration regressions (filters, fallback states) must remain protected.
