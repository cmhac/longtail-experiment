# Research: Mobile Sidebar Navigation Drawer

## Decision 1: Activation range for drawer behavior

- Decision: Apply mobile drawer behavior to phone and small-tablet viewports; keep desktop navbar behavior unchanged.
- Rationale: The feature intent is to eliminate clutter from the current multi-row small-screen top nav while preserving desktop interaction patterns.
- Alternatives considered:
  - Phone-only activation: rejected because it leaves clutter risk on small tablets.
  - All viewports: rejected because spec explicitly preserves desktop behavior.

## Decision 2: Drawer width and visual treatment

- Decision: Drawer occupies about 90% of viewport width and opens from the right, leaving a visible blurred sliver of background.
- Rationale: This satisfies the clarified requirement for "nearly all" coverage while preserving contextual orientation to underlying page content.
- Alternatives considered:
  - 85% width: rejected as potentially exposing too much background.
  - 95% width: rejected as reducing visible contextual sliver.

## Decision 3: Navigation interaction behavior

- Decision: Tapping any destination item closes the drawer immediately and then navigates.
- Rationale: Immediate close avoids stale overlay states and gives a predictable mobile transition behavior.
- Alternatives considered:
  - Close after route load: rejected due to transition inconsistency.
  - Keep open until manual close: rejected due to unnecessary interaction friction.

## Decision 4: Auth-protected interaction handling

- Decision: Signed-out users tapping protected actions are redirected to `/login`; sign-out from drawer routes to `/`.
- Rationale: This matches clarified UX rules and keeps auth boundary behavior explicit and testable.
- Alternatives considered:
  - Inline sign-in prompt in drawer: rejected as additional surface complexity beyond scope.
  - Hiding all protected actions: rejected because spec expects explicit protected-action handling.

## Decision 5: Reuse vs duplication in header utilities

- Decision: Reuse existing notification, comparison, and auth/session logic from `SiteHeader` and compose drawer-specific presentation around those sources.
- Rationale: Avoids divergence of count/session semantics and aligns with repository shared-component conventions.
- Alternatives considered:
  - Separate mobile-only utility state: rejected due to consistency and maintenance risks.

## Decision 6: Styling approach for drawer

- Decision: Keep shell responsive behavior in existing global shell style surface and implement reusable drawer UI via HeroUI/Tailwind-compatible shared components.
- Rationale: Aligns with constitution/frontend conventions and existing shell contract tests.
- Alternatives considered:
  - Feature-local standalone CSS file: rejected due to UI system consistency constraints.
  - Entirely inline utility classes in `SiteHeader`: rejected because repeated drawer sections should be shared abstractions.
