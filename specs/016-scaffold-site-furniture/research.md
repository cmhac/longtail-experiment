# Research: Minimal Site Furniture Shell

## Decision 1: Use the existing global app shell entry points for furniture composition

- Decision: Implement the header, main placeholder, and footer using the existing frontend app layout composition boundaries.
- Rationale: This keeps the scaffold centralized, avoids duplicate page-level shell logic, and aligns with current frontend architecture.
- Alternatives considered:
  - Build shell regions directly in a single route page.
    - Rejected because shell responsibilities should remain in global layout boundaries.
  - Delay shell composition until feature pages exist.
    - Rejected because this feature exists specifically to establish baseline furniture first.

## Decision 2: Prefer HeroUI components for shell primitives wherever equivalents exist

- Decision: Build shell furniture from HeroUI primitives and composition patterns where those primitives match required behavior.
- Rationale: This enforces consistency with the project UI system and avoids unnecessary custom UI divergence.
- Alternatives considered:
  - Use only raw HTML elements with custom classes.
    - Rejected because it underuses the approved UI system and increases future restyling effort.
  - Introduce additional third-party component libraries.
    - Rejected because scope calls for HeroUI-first usage and minimal complexity.

## Decision 3: Enforce monochromatic visual language through shell-level style rules

- Decision: Restrict shell-level styles to neutral monochrome tokens/classes and disallow accent-colored variants in shell furniture.
- Rationale: The feature explicitly requires an intentionally minimal monochromatic baseline.
- Alternatives considered:
  - Allow selective accent use for brand emphasis.
    - Rejected because it violates explicit scope requirements.
  - Leave color choices unconstrained for later cleanup.
    - Rejected because unconstrained baseline styling creates drift and rework.

## Decision 4: Support light/dark mode via device preference from initial render

- Decision: Use preference-aware mode behavior that follows device/browser light-dark preference by default.
- Rationale: This satisfies accessibility and usability expectations at launch with no extra user setup.
- Alternatives considered:
  - Ship light mode only and add dark mode later.
    - Rejected because the feature requires both from the beginning.
  - Require manual toggle as the only theme mechanism.
    - Rejected because device preference awareness is required baseline behavior.

## Decision 5: Validate with structure + appearance behavior tests and local runtime checks

- Decision: Add automated checks for shell region presence and theme behavior, plus local verification steps for light/dark and monochrome compliance.
- Rationale: This combines enforceable regressions with practical visual verification.
- Alternatives considered:
  - Rely only on manual UI inspection.
    - Rejected because it does not provide stable regression protection.
  - Test only shell structure and skip appearance behavior.
    - Rejected because monochrome and preference-aware theming are core requirements.
