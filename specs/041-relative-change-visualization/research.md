# Research: Relative Change Visualizations

## Decision 1: Canonical percentage formula uses signed baseline-relative change

- Decision: Use signed baseline-relative percent change: ((current value - baseline value) / baseline value) \* 100.
- Rationale: This is the most widely understood meaning of relative change and preserves directionality for decline/growth analysis.
- Alternatives considered:
  - Absolute percentage change: rejected because it hides direction.
  - Symmetric percent difference: rejected because it diverges from user expectation for baseline comparison.

## Decision 2: Support both fixed-baseline selectors

- Decision: Fixed-baseline mode supports baseline selection by exact available date and by observation index/offset.
- Rationale: Date selection aligns with time-based analysis (for example ten years ago), while index/offset supports cadence-agnostic workflows.
- Alternatives considered:
  - Date-only selector: rejected because users also requested offset-based baseline reference.
  - Offset-only selector: rejected because users need explicit historical anchor semantics.

## Decision 3: Non-computable points remain timeline gaps

- Decision: Keep non-computable points in chronological position as unavailable gaps and do not coerce fallback numeric values.
- Rationale: Preserves timeline continuity while avoiding misleading values.
- Alternatives considered:
  - Drop points entirely: rejected because it distorts temporal continuity.
  - Force 0% or carry-forward values: rejected because both produce false analytical signals.

## Decision 4: Preserve baseline settings across scope changes when valid

- Decision: Keep selected baseline mode/parameters through time-range or filter changes if still valid; if invalid, keep settings visible and show explicit unavailable state.
- Rationale: Prevents user surprise while preserving transparency when a selection can no longer compute.
- Alternatives considered:
  - Silent auto-adjustment: rejected because it obscures what baseline is actually used.
  - Always reset to defaults: rejected because it causes unnecessary context loss.

## Decision 5: Exact-match-only baseline date behavior

- Decision: Date-based fixed baseline is exact-match only and the UI offers only dates that exist in the active observation scope.
- Rationale: Eliminates ambiguous nearest-neighbor behavior and keeps date-to-observation mapping deterministic.
- Alternatives considered:
  - Nearest earlier date fallback: rejected by clarification decision.
  - Nearest any-direction fallback: rejected because it introduces hidden baseline drift.

## Decision 6: Implementation discipline is mandatory process policy for this feature

- Decision: Execute in stable slices with regular commits, red/green TDD, and manual local verification after each slice; frontend slices require browser-tool validation.
- Rationale: User requested explicit delivery discipline and this lowers regression risk for interactive chart behavior.
- Alternatives considered:
  - Single large implementation commit: rejected by user instruction and debugging risk.
  - Test-after-implementation only: rejected in favor of red/green TDD for behavior correctness.
