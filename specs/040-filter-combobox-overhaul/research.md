# Research: Filter Combobox Overhaul

## Decision 1: Treat filter correctness as a cross-layer bug, not a presentation-only bug

- **Decision**: Fix source/category/sort behavior by tracing the full catalog path across URL params, frontend request wiring, backend query normalization, repository filtering, and rendered rows.
- **Rationale**: Browser testing already showed that URL state changes occur while visible dataset rows do not change. That failure can only be resolved reliably by validating the full flow rather than patching one layer in isolation.
- **Alternatives considered**:
  - Patch only the frontend rendering path: rejected because it risks hiding backend query mismatches.
  - Patch only the backend repository path: rejected because the observed failure may also involve request-param wiring or stale render state.

## Decision 2: Keep combobox option narrowing local to the loaded option set

- **Decision**: Implement in-box combobox filtering as local option narrowing on the already available option arrays.
- **Rationale**: The feature specification explicitly allows client-side narrowing for dropdown options. The option sets are already available when the page renders, so local narrowing is the smallest change that restores expected searchable-combobox behavior.
- **Alternatives considered**:
  - Add a dedicated async option-search endpoint: rejected because it expands scope without a documented need.
  - Leave narrowing behavior untouched and rely only on direct option browsing: rejected because the controls already present themselves as searchable comboboxes.

## Decision 3: Separate behavior repair from visual polish in both sequencing and commits

- **Decision**: Implement in three slices: filter correctness first, combobox narrowing second, dark-mode/active-state polish third, with a distinct commit after each stable slice.
- **Rationale**: The user explicitly requested that work not land as one large commit. Separating the slices keeps failures attributable, makes review easier, and reduces the chance that styling changes mask unresolved behavior bugs.
- **Alternatives considered**:
  - Deliver one combined refactor with one commit: rejected by user instruction and by the debugging risk.
  - Lead with visual polish first: rejected because it improves appearance while the core controls remain untrustworthy.

## Decision 4: Use thicker border width as the active-state treatment

- **Decision**: Replace the current active highlight treatment with increased border width on the active combobox.
- **Rationale**: The requested interaction change is specific and simpler than introducing an additional decorative active layer. Border-width emphasis also fits the existing control structure without requiring a new visual pattern.
- **Alternatives considered**:
  - Retune the current active highlight: rejected because the user explicitly requested a different active-state signal.
  - Introduce a new filled or glowed active background: rejected because it increases visual complexity and dark-mode contrast risk.

## Decision 5: Preserve existing discovery contracts and adjust them only where result alignment requires it

- **Decision**: Keep the existing catalog response shape unless a contract-level mismatch is required to fix the observed filter behavior.
- **Rationale**: The feature is about restoring correct behavior and polishing interaction states, not redesigning the discovery API. Existing consumers should stay stable wherever possible.
- **Alternatives considered**:
  - Redesign catalog payload semantics broadly: rejected as unnecessary scope expansion.
  - Avoid documenting contract expectations because the payload shape already exists: rejected because explicit contract notes help prevent regressions in future filter work.
