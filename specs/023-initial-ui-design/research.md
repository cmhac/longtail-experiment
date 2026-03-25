# Research: Initial UI Design Navbar Slice

## Decision 1: Header ownership and component integration

- Decision: Implement the navbar inside the existing shell header component (`SiteHeader`) rather than creating a separate top-level app layout abstraction.
- Rationale: The current shell already defines semantic header ownership and is rendered on the home page; extending it minimizes surface area and keeps tests localized.
- Alternatives considered:
  - New shared app-level layout wrapper: more flexible long term, but unnecessary complexity for an initial single-slice navbar.
  - Injecting navbar directly into page component: faster initially, but weakens shell boundaries and duplicates structure responsibility.

## Decision 2: Navigation state model for in-scope vs out-of-scope controls

- Decision: Model tabs/icon controls with explicit enabled/disabled and active states where Home is active/enabled, Datasets and Trends are disabled, and search is disabled.
- Rationale: This enforces scope boundaries from the spec and avoids false affordances while preserving visible IA placeholders.
- Alternatives considered:
  - Hide out-of-scope controls entirely: reduces confusion but violates explicit requirement to show disabled controls.
  - Render controls as enabled and no-op on click: appears broken and creates accessibility ambiguity.

## Decision 3: Home navigation behavior

- Decision: Brand label and Home tab both resolve to homepage navigation behavior via safe Next.js route navigation semantics.
- Rationale: Aligns with FR-008 while keeping a consistent, expected click target for users.
- Alternatives considered:
  - Brand-only navigation: fails explicit requirement that Home tab also routes to home.
  - Home tab-only navigation: weakens discoverability and contradicts user-request interpretation in assumptions.

## Decision 4: Profile dropdown placeholder implementation

- Decision: Use a lightweight anchored dropdown/menu interaction on the profile icon that renders exactly one message item: `dropdown coming soon`.
- Rationale: Creates a stable interaction anchor for future account features while keeping feature scope intentionally narrow.
- Alternatives considered:
  - Static tooltip text instead of dropdown: does not satisfy required dropdown interaction.
  - Full account menu scaffold: over-scoped for this slice.

## Decision 5: Light/dark and responsive baseline

- Decision: Keep existing theme token source-of-truth and extend shell/header styles to ensure contrast and readability in both light and dark modes, with narrow-width-safe wrapping/spacing.
- Rationale: Reuses current appearance model and avoids introducing competing theme systems.
- Alternatives considered:
  - New independent navbar theme tokens: duplicates theme logic and increases drift risk.
  - Desktop-only first pass: fails narrow viewport edge-case requirement.

## Decision 6: Testing strategy

- Decision: Add/adjust contract-level and interaction tests in frontend test suite to verify required structure, disabled behavior, homepage navigation targets, and placeholder dropdown content.
- Rationale: Contract tests are robust for this UI slice and support maintaining coverage thresholds.
- Alternatives considered:
  - Manual-only validation: insufficient against constitution quality and coverage expectations.
  - Broad e2e-only coverage: slower and less precise for quick navbar state regressions.
