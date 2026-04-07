# Data Model: Mobile Sidebar Navigation Drawer

## Overview

This feature introduces a UI interaction model (not persistent database entities) for mobile navigation drawer behavior in the shared site header.

## Entity: MobileDrawerState

- Purpose: Represents current drawer visibility and interaction state in the header.
- Fields:
  - `isOpen` (boolean): Whether the drawer is currently open.
  - `isAnimating` (boolean, optional): Transitional state for open/close motion handling.
  - `lastAction` (enum, optional): Last drawer action (`open`, `close`, `navigate`, `dismiss`).
- Validation rules:
  - `isOpen=true` requires backdrop to block background interaction.
  - Opening is only enabled in the phone+small-tablet responsive range.

## Entity: DrawerMenuItem

- Purpose: Defines one navigable row in the drawer.
- Fields:
  - `key` (string): Stable identifier (`account`, `comparison`, `search`, `home`, `sources`, `datasets`, `admin`, `sign_out`).
  - `label` (string): User-visible row label.
  - `destination` (string | null): Route target when applicable.
  - `isProtected` (boolean): Whether auth is required.
  - `isVisible` (boolean): Visibility after role/session filtering.
  - `orderIndex` (number): Required order in rendered stack.
- Validation rules:
  - Primary row order must remain fixed:
    1. Header row (logo + bell)
    2. Account
    3. Comparison (with counter)
    4. Search
    5. Home
    6. Sources
    7. Datasets
  - Footer row order must remain fixed: optional `admin` above `sign_out`.

## Entity: DrawerUtilityState

- Purpose: Projects existing utility values/permissions into drawer UI.
- Fields:
  - `comparisonCount` (number): Current selected dataset count from comparison state.
  - `unreadNotificationCount` (number): Current unread notification count when available.
  - `authStatus` (enum): `signed_in` | `signed_out`.
  - `privilegeLevel` (enum | null): `standard` | `admin` | `owner` | `null`.
- Validation rules:
  - `comparisonCount` must mirror existing comparison counter semantics.
  - `admin` action visibility requires `privilegeLevel` in (`admin`, `owner`).
  - Signed-out + protected action triggers login redirect behavior.

## State Transitions

1. `closed` -> `open`
   - Trigger: Hamburger control activation within mobile activation range.
   - Effects: Drawer visible (~90% width), backdrop visible, background interaction disabled.

2. `open` -> `closed` via dismiss
   - Trigger: Explicit close control, backdrop dismiss, or escape interaction (if supported).
   - Effects: Drawer hidden, backdrop removed, background interaction restored.

3. `open` -> `closed` via navigation
   - Trigger: Any destination row selection.
   - Effects: Drawer closes immediately, then navigation proceeds.

4. `open` -> `closed` via sign-out
   - Trigger: Sign out row selection while signed in.
   - Effects: Session cleared, drawer closes, redirect to `/`.

5. `open` + signed-out protected tap
   - Trigger: Protected row selection while signed out.
   - Effects: Redirect to `/login`.
