# Data Model: Global Page Content Width

## Entity: Global Content Width Policy

- Purpose: Defines the default width behavior for shell page content regions.
- Fields:
  - policy_key: Stable identifier for the default policy.
  - max_content_width: Maximum readable content width at larger viewport sizes.
  - horizontal_alignment: Default centering behavior for constrained content.
  - applies_to: Set of default shell content regions that inherit the policy.
- Validation Rules:
  - max_content_width must represent a finite positive width.
  - applies_to cannot be empty for a valid default policy.

## Entity: Page Layout Region

- Purpose: Represents a concrete render region on a shell page.
- Fields:
  - region_key: Stable identifier (for example, page main content, feed section, list section).
  - page_scope: Route or shell scope where region is rendered.
  - width_mode: constrained_default or explicit_full_width.
  - parent_region: Optional parent region that provides inherited layout context.
- Validation Rules:
  - width_mode must be one of the allowed modes.
  - region must resolve to one effective width mode at runtime.

## Entity: Full-Width Exception

- Purpose: Explicitly marks a region that bypasses default constrained behavior.
- Fields:
  - exception_key: Stable identifier for exception entry.
  - target_region_key: Region receiving full-width behavior.
  - reason: Human-readable reason for exception designation.
  - review_scope: Route or shell areas where exception applies.
- Validation Rules:
  - target_region_key must reference an existing page layout region.
  - reason must be present to avoid implicit or accidental exceptions.

## Entity: Layout Validation Scenario

- Purpose: Defines testable expectations for width behavior across routes and viewport sizes.
- Fields:
  - scenario_key: Stable identifier.
  - route: Route under test.
  - viewport_class: wide_desktop or narrow/mobile.
  - expected_default_behavior: Constrained-width expectation for default regions.
  - expected_exceptions: Explicit full-width regions that must remain edge-to-edge.
- Validation Rules:
  - Each scenario must include at least one default constrained region assertion.
  - Any full-width expectation must map to an explicit exception entry.

## Relationships

- A Global Content Width Policy applies to many Page Layout Regions by default.
- A Full-Width Exception overrides width mode for one or more target Page Layout Regions.
- A Layout Validation Scenario verifies one route against both default policy behavior and exception behavior.
