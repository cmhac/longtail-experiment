# Contract: Mobile Sidebar Drawer UI Behavior

## Purpose

Define the user-visible and testable behavior contract for the shared small-screen navigation drawer in the site header.

## Scope

- Applies to pages rendered with shared site shell header.
- Applies to phone and small-tablet viewport range.
- Desktop navbar behavior remains unchanged.

## Drawer Entry Contract

- A hamburger control is visible in activation range and opens the drawer from the right.
- Opening the drawer displays a backdrop where:
  - A visible background sliver remains.
  - Background is blurred.
  - Background content is not interactable.

## Layout and Ordering Contract

Drawer content order from top to bottom:

1. Header row: Longtail logo (left), notifications bell icon (right)
2. Account button
3. Comparison button with compared dataset counter
4. Search button
5. Home button
6. Sources button
7. Datasets button
8. Footer area:
   - Admin button only when user privilege is admin/owner
   - Sign out button always present below Admin when Admin is present

## Interaction Contract

- Selecting any destination row closes the drawer immediately before navigation transition.
- Comparison counter value matches existing comparison state semantics used in header.
- Notifications bell behavior and unread semantics remain consistent with existing header notification behavior.
- Sign out from drawer clears session and redirects to `/`.
- Signed-out user selecting protected actions is redirected to `/login`.

## Visibility and Access Contract

- Admin action is visible only for admin/owner sessions.
- Admin action is hidden for non-admin signed-in users and signed-out users.
- Protected action handling must never expose private content to signed-out users.

## Regression Contract

- Existing desktop navigation structure remains unchanged.
- Existing header utility semantics (comparison count, notifications, auth role display) remain authoritative.
- Shared shell test markers remain stable unless intentionally revised in corresponding tests.
