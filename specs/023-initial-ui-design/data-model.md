# Data Model: Initial UI Design Navbar Slice

## Overview

This feature defines UI interaction/state entities for the top navigation bar. No database schema or backend contract changes are introduced.

## Entities

### 1. NavigationBar

- Description: Top-level shell header surface that arranges brand, primary tabs, and utility controls.
- Fields:
  - region_key (string, required): shell region identifier (`header`).
  - full_width (boolean, required): always true for this feature.
  - appearance_mode (enum, required): `light` or `dark`.
  - brand_label (string, required): `Longtail`.
- Validation rules:
  - Must render on home page shell with semantic header landmark.
  - Must remain readable in both appearance modes.

### 2. NavigationTab

- Description: Individual primary navigation control in the navbar tab group.
- Fields:
  - key (enum, required): `home`, `datasets`, or `trends`.
  - label (string, required): display text for the tab.
  - is_active (boolean, required)
  - is_enabled (boolean, required)
  - target_route (string, optional): route when enabled (required for `home`, absent for disabled tabs).
- Validation rules:
  - Exactly three tabs must be present: Home, Datasets, Trends.
  - Home must be enabled and active for this initial slice.
  - Datasets and Trends must be disabled and must not trigger navigation.

### 3. UtilityIconControl

- Description: Icon button in right-side utility group.
- Fields:
  - key (enum, required): `search` or `profile`.
  - is_enabled (boolean, required)
  - icon_name (string, required)
  - action_type (enum, required): `none` or `open_dropdown`.
- Validation rules:
  - Search control is present but disabled (`is_enabled=false`, `action_type=none`).
  - Profile control is enabled and opens contextual dropdown.

### 4. ProfileDropdownPanel

- Description: Contextual overlay anchored to profile control.
- Fields:
  - anchor_control_key (string, required): `profile`.
  - is_open (boolean, required)
  - content_items (array<string>, required)
- Validation rules:
  - When opened, panel must contain exactly one text item: `dropdown coming soon`.
  - No additional actionable menu items are present in this feature slice.

## Relationships

- NavigationBar 1-to-many NavigationTab.
- NavigationBar 1-to-many UtilityIconControl.
- UtilityIconControl (`profile`) 1-to-1 ProfileDropdownPanel.

## State Transitions

### Navbar interaction lifecycle

1. initialized: Navbar renders with Home active, Datasets/Trends disabled, search disabled.
2. home_navigation: User selects brand label or Home tab and remains on/returns to homepage.
3. disabled_interaction: User selects Datasets/Trends/search and state remains unchanged with no navigation/action.
4. profile_dropdown_open: User selects profile icon; dropdown opens with placeholder content.
5. profile_dropdown_closed: User dismisses or toggles profile interaction; dropdown closes without side effects.
