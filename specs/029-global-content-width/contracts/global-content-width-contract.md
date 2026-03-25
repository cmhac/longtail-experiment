# Contract: Global Content Width Behavior

## Purpose

Define layout behavior expectations for default constrained shell content width and explicit full-width exceptions.

## Contract Scope

- Applies to shell-based user-facing pages.
- Applies to default page content regions unless explicitly overridden.
- Covers home and datasets list routes as required baseline verification targets.

## Width Modes

### 1. constrained_default

- Description: Region inherits the global max-content-width and centered alignment behavior.
- Required Behavior:
  - Region is explicitly marked with the constrained mode class marker.
  - Region does not expand edge-to-edge on wide desktop displays.
  - Region remains horizontally centered in viewport.
  - Region fills available width naturally on narrow viewports.

### 2. explicit_full_width

- Description: Region is intentionally designated to bypass constrained default behavior.
- Required Behavior:
  - Region is explicitly marked with the full-width mode class marker.
  - Region spans full available viewport width for its surface.
  - Region does not implicitly alter neighboring constrained regions.
  - Exception designation is explicit and reviewable.

## Route-Level Expectations

### Home Route

- Main content sections inherit constrained_default behavior.
- Intentionally full-width shell bands retain explicit_full_width behavior.

### Datasets List Route

- Main listing content and controls inherit constrained_default behavior.
- Intentionally full-width shell bands retain explicit_full_width behavior.

## Validation Contract

A feature implementation is compliant when all statements below are true:

1. Default shell content regions on both home and datasets list routes are constrained and centered on wide desktop viewports.
2. Explicit full-width exception regions remain edge-to-edge where designated.
3. No regressions in page behavior (navigation, list controls, fallback states) are introduced by width-mode changes.
4. Responsive behavior remains readable at narrower viewport sizes.
