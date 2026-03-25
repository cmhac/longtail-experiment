# Research: Global Page Content Width

## Decision 1: Set one shared default constrained content width for shell page content

- Decision: Use one global default content width policy for shell page content regions so pages inherit a consistent readable desktop width.
- Rationale: Current shell page content can expand to full available width on large monitors, reducing readability and visual consistency between routes.
- Alternatives considered:
  - Tune width independently per page: rejected because this increases drift and maintenance overhead.
  - Keep current full-width behavior: rejected because it does not address wide-screen readability concerns.

## Decision 2: Preserve intentional full-width bands via explicit exceptions

- Decision: Keep intentionally full-width shell regions (for example, top and bottom shell bands) as explicit exceptions rather than changing all surfaces to constrained width.
- Rationale: Some shell surfaces are intentionally edge-to-edge for visual framing and identity continuity.
- Alternatives considered:
  - Constrain every region by default with no exceptions: rejected because it would break intentional full-bleed shell composition.
  - Implicitly infer full-width exceptions from existing styles: rejected because hidden inference is brittle and hard to validate.

## Decision 3: Validate width policy through structural and viewport checks

- Decision: Add coverage that verifies constrained defaults and explicit full-width exceptions across representative shell routes, then confirm manually on wide desktop and narrow viewports.
- Rationale: Width behavior can regress silently without direct assertions, especially when future pages are added.
- Alternatives considered:
  - Manual validation only: rejected because it is not durable and can miss regressions.
  - Snapshot-only verification: rejected because visual snapshots alone may not encode layout intent clearly.
