# Contract: Minimal Shell Structure and Theme Behavior

## Purpose

Define required shell structure and appearance behavior for the initial minimal UI baseline.

## Scope

- Required shell regions: header, main placeholder, footer.
- Monochromatic appearance rules for shell-level UI.
- Device preference-aware light/dark behavior.
- Verification requirements for local and automated checks.

## Contract Definitions

### 1) Shell Region Presence Contract

Requirements:

- The root shell must render three visible regions: header, main placeholder, and footer.
- Region order must remain header -> main placeholder -> footer.
- Main placeholder must communicate that feature content will be added later.

Validation outcomes:

- Invalid when any required region is missing.
- Invalid when region order is broken.
- Invalid when placeholder messaging is absent.

### 2) Monochrome Appearance Contract

Requirements:

- Shell-level styling uses monochromatic visual language only.
- Accent-colored shell variants, highlights, or decorative treatments are not permitted.
- Header, main placeholder, and footer all follow the same neutral palette family.

Validation outcomes:

- Invalid when any shell region introduces accent color usage.
- Invalid when shell regions diverge from monochromatic rules.

### 3) Device Preference Theme Contract

Requirements:

- Shell defaults to device/browser preference-aware appearance mode.
- Light preference renders shell in light mode; dark preference renders shell in dark mode.
- In both modes, shell text and surfaces remain readable.

Validation outcomes:

- Invalid when light/dark preference is not respected.
- Invalid when readability fails in either mode.

### 4) Verification Contract

Requirements:

- Local startup must load root shell without runtime-blocking errors.
- Automated checks must verify region presence and theme behavior expectations.
- Quality gates for affected scope must pass without suppression.

Validation outcomes:

- Invalid when startup fails under documented steps.
- Invalid when contract-focused tests fail.
- Invalid when affected lint/format/typecheck/test/coverage checks fail.

## Non-Goals

- Product feature content in the main region.
- Manual theme toggle workflows.
- New persistence or API behavior.

## Evidence Expectations

Acceptance evidence should include:

- Visual confirmation of header, main placeholder, and footer.
- Automated verification of shell presence and theme behavior.
- Local runtime startup success.
- Passing affected quality gate results.
