# Research: Dataset List Page

## Decision 1: Keep datasets page as the primary catalog entry point

- Decision: Extend the existing datasets route instead of introducing a second catalog page.
- Rationale: Preserves navigation expectations and minimizes duplication in discovery experiences.
- Alternatives considered:
  - Add a separate list route and deprecate current route: introduces migration overhead and split behavior.
  - Keep current route unchanged and add only visual polish: does not satisfy required filtering/sorting interaction scope.

## Decision 2: Consolidate listing controls into one toolbar region

- Decision: Provide source, category, and sort controls in a single stable control strip near the top of the list.
- Rationale: Improves scanability and keeps control semantics predictable across desktop and mobile layouts.
- Alternatives considered:
  - Split controls across different sections: increases cognitive load and weakens discoverability.
  - Hide controls behind advanced options: conflicts with screenshot-driven usability direction.

## Decision 3: Define card metadata guarantees explicitly

- Decision: Each dataset card includes source badge, title, summary, tags, and last-updated context.
- Rationale: Users need consistent metadata to quickly compare entries and choose what to open.
- Alternatives considered:
  - Title-only card treatment: insufficient for decision-making.
  - Deep metadata density in each card: reduces readability and slows scanning.

## Decision 4: Preserve recency-first list ordering by default

- Decision: Default sorting is recency-first while retaining user-selectable sort choices.
- Rationale: Catalog discovery prioritizes freshness and aligns with screenshot expectations.
- Alternatives considered:
  - Alphabetical default ordering: weaker for frequent returning users scanning updates.
  - Hidden sort behavior without visible control: lowers user trust in list ordering.

## Decision 5: Empty and fallback states are first-class outcomes

- Decision: Keep explicit empty-results and error-safe rendering states in the listing flow.
- Rationale: Control combinations can produce no matches; users need clear guidance without blocked navigation.
- Alternatives considered:
  - Silent empty lists with no message: unclear and low trust.
  - Full-page failure on list fetch errors: disproportionate impact for a single surface.

## Decision 6: Validation remains frontend-focused with contract-aware tests

- Decision: Add page/component/client tests to enforce listing hierarchy, control behavior, and result-state transitions.
- Rationale: This feature is primarily frontend behavior over existing catalog contracts.
- Alternatives considered:
  - Manual-only QA: insufficient for coverage and stop-gate requirements.
  - Backend-only testing: does not validate page-level usability and control interactions.
