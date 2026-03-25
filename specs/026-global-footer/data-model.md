# Data Model: Global Footer Component

## Overview

This feature introduces a global footer presentation model for all shell-rendered pages.

## Entities

### 1. FooterSection

- Description: The persistent bottom-of-page shell region.
- Fields:
  - section_id (string, required)
  - visible_on_shell_pages (boolean, required)
  - layout_mode (enum: full_width, required)
  - content (FooterContentBlock, required)
- Validation rules:
  - Must render on every page using the site shell.
  - Must appear after main content region.

### 2. FooterContentBlock

- Description: Editorial content bundle displayed inside the footer.
- Fields:
  - brand_text (string, required)
  - mission_text (string, required)
  - alignment (enum: left_aligned, required)
- Validation rules:
  - brand_text must be non-empty.
  - mission_text must be non-empty and readable in wrapped form.

### 3. FooterPresentationState

- Description: Presentation conditions for theme and viewport readability.
- Fields:
  - theme_mode (enum: light, dark)
  - viewport_mode (enum: desktop, mobile)
  - readable (boolean, required)
- Validation rules:
  - readable must remain true across supported theme and viewport modes.
  - no overlap/clipping in mobile mode.

## Relationships

- FooterSection has exactly one FooterContentBlock.
- FooterSection is rendered once per shell page instance.
- FooterPresentationState applies to FooterSection rendering conditions.

## State Transitions

1. shell page render -> footer rendered with content block.
2. theme switch (light/dark) -> footer re-renders with preserved readability.
3. viewport change (desktop/mobile) -> footer reflows while preserving hierarchy.
