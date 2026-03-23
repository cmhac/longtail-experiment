# Data Model: Minimal Site Furniture Shell

## Overview

This feature introduces presentation-level entities for shell structure, monochrome appearance rules, and preference-aware light/dark rendering behavior.

## Entities

### 1) SiteShell

Represents the global page frame rendered at initial load.

Fields:

- shell_id: string (required, root shell identifier)
- shell_status: enum { draft, renderable, verified } (required)
- regions: list[ShellRegion] (required)
- appearance_mode: AppearanceMode (required)

Validation rules:

- regions must include exactly: header, main_placeholder, footer.
- shell_status can transition to verified only after structure and appearance checks pass.

Relationships:

- One SiteShell contains many ShellRegion records.
- One SiteShell is validated by one or more VerificationScenario records.

### 2) ShellRegion

Represents one structural section of the site shell.

Fields:

- region_id: string (required)
- region_name: enum { header, main_placeholder, footer } (required)
- display_order: integer (required)
- visibility_state: enum { visible, hidden, failed } (required)
- content_kind: enum { identity, placeholder, informational } (required)

Validation rules:

- display_order must be unique within a shell.
- visibility_state failed invalidates shell verification.
- content_kind must align with region_name semantics.

Relationships:

- Each ShellRegion belongs to one SiteShell.

### 3) AppearanceMode

Represents active theme mode resolved from user environment preference.

Fields:

- mode_id: string (required)
- mode_name: enum { light, dark } (required)
- source: enum { device_preference } (required)
- contrast_status: enum { valid, invalid } (required)

Validation rules:

- source remains device_preference for this feature scope.
- contrast_status must be valid in all shell regions for acceptance.

Relationships:

- One AppearanceMode is applied to one SiteShell per render session.

### 4) MonochromeStyleRule

Represents shell styling constraints that prohibit accent color usage.

Fields:

- rule_id: string (required)
- scope: enum { header, main_placeholder, footer, global_shell } (required)
- palette_type: enum { monochrome_only } (required)
- accent_usage_allowed: boolean (required)

Validation rules:

- palette_type must remain monochrome_only in this feature.
- accent_usage_allowed must be false for all shell scopes.

Relationships:

- Multiple MonochromeStyleRule records constrain one SiteShell.

### 5) VerificationScenario

Represents repeatable shell acceptance checks.

Fields:

- scenario_id: string (required)
- verification_type: enum { structure, monochrome_compliance, theme_preference } (required)
- expected_outcome: string (required)
- result_state: enum { pass, fail } (required)

Validation rules:

- structure must pass before shell_status can become verified.
- monochrome_compliance and theme_preference must both pass before final acceptance.

Relationships:

- VerificationScenario validates SiteShell behavior for a specific run.

## State Transitions

### SiteShell Lifecycle

1. draft: shell definitions exist but are not validated.
2. renderable: shell renders all required regions.
3. verified: structure, monochrome compliance, and theme preference checks pass.

Transition constraints:

- draft -> verified requires intermediate renderable state.
- any failed verification scenario blocks verified state.

## Invariants

- Header, main placeholder, and footer are always present in stable order.
- Shell styling is monochromatic with no accent-colored shell elements.
- Active appearance mode follows device preference between light and dark.
- Shell remains readable in both appearance modes.
