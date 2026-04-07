# Feature Specification: Mobile Sidebar Navigation Drawer

**Feature Branch**: `[049-mobile-sidebar-drawer]`  
**Created**: 2026-04-06  
**Status**: Draft  
**Input**: User description: "We’re going to create a new mobile sidebar menu in lieu of the current implementation of the mobile top nav. In the current implementation, we often end up with 3 rows of items in the top nav and it looks very cluttered. In this new spec, we’ll create a small screen-focused change that will use a hamburger icon to show a tray that will slide in from the right of the screen. It should cover nearly all of the screen with a slight bit of the screen behind the tray visible, but blurred. That sidebar should contain the following, in this order from top to bottom: 1) Longtail logo row with bell icon, 2) account, 3) comparison with counter, 4) search, 5) home, 6) sources, 7) datasets, and at the bottom optional admin button then sign out."

## Clarifications

### Session 2026-04-06

- Q: At what viewport condition should the drawer replace the current top-nav pattern? → A: Include both phone and small tablet widths.
- Q: What coverage target should define "nearly all" for open drawer width? → A: About 90% of viewport width.
- Q: What should happen to the drawer immediately after tapping a destination item? → A: Drawer closes immediately.
- Q: Where should users land immediately after sign-out from the drawer? → A: Redirect to Home page.
- Q: What should happen when a signed-out user taps an auth-protected drawer action? → A: Redirect to Login page.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Replace Cluttered Mobile Top Navigation (Priority: P1)

As a mobile user, I want a hamburger-triggered sidebar drawer so I can access key navigation actions from a clean, single-column menu instead of a crowded multi-row top bar.

**Why this priority**: This is the core user-facing problem being solved: reducing clutter and improving navigation clarity on small screens.

**Independent Test**: Can be fully tested by opening the app on a small-screen viewport, opening the drawer from the hamburger control, and confirming all required menu rows appear in the specified top-to-bottom order.

**Acceptance Scenarios**:

1. **Given** a user is on a small-screen viewport, **When** they tap the hamburger control, **Then** a right-side drawer appears and the screen behind it remains partially visible with a blurred treatment.
2. **Given** the drawer is open, **When** the user views the first row, **Then** the Longtail logo appears on the left and a bell icon appears on the right.
3. **Given** the drawer is open, **When** the user scans the primary menu rows, **Then** the rows appear in this exact order: Account, Comparison, Search, Home, Sources, Datasets.
4. **Given** the drawer is open, **When** the user selects any primary menu button, **Then** the drawer closes immediately and the user is routed to the corresponding page.

---

### User Story 2 - Keep Utility Actions Available In Drawer (Priority: P2)

As a signed-in user, I want account, comparison status, notifications access, and sign-out actions in the mobile drawer so I can complete common account and navigation tasks from one place.

**Why this priority**: The new navigation pattern must preserve current utility behavior and avoid regressions in critical user actions.

**Independent Test**: Can be tested by opening the mobile drawer while signed in, confirming comparison count visibility, account and sign-out actions, and successful routing/action results.

**Acceptance Scenarios**:

1. **Given** the drawer is open, **When** the user views the comparison row, **Then** it shows the compared dataset counter with the same count semantics currently used in top navigation.
2. **Given** a signed-in user opens the drawer, **When** they tap Account, **Then** they are taken to the account settings page.
3. **Given** a signed-in user opens the drawer, **When** they tap Sign out at the bottom section, **Then** their session is ended and they are redirected to the Home page in signed-out state.
4. **Given** the drawer is open, **When** the user taps the bell icon in the top row, **Then** they can access notification behavior consistent with existing in-app notifications entry.
5. **Given** the drawer is open and notification data changes, **When** the user views the bell row state, **Then** unread badge visibility and bell toggle behavior remain consistent with the existing header notification control.

---

### User Story 3 - Respect Role-Specific Actions In Drawer (Priority: P3)

As an admin user, I want the admin destination available in the drawer footer so I can reach admin tools from mobile without exposing admin-only actions to non-admin users.

**Why this priority**: This preserves role-based access behavior and ensures the mobile navigation remains aligned with existing authorization boundaries.

**Independent Test**: Can be tested by opening the drawer as an admin and as a non-admin user and verifying admin action visibility only for eligible users.

**Acceptance Scenarios**:

1. **Given** an admin user opens the drawer, **When** they view the bottom section, **Then** an Admin button appears above Sign out.
2. **Given** a non-admin user opens the drawer, **When** they view the bottom section, **Then** no Admin button is shown.
3. **Given** an admin taps the Admin button, **When** routing completes, **Then** they arrive at the admin landing experience.

### Edge Cases

- Drawer opens on a small screen while the user has zero comparison datasets selected; the comparison row still renders and shows a zero-state count.
- Drawer opens while notification summary data is still loading; bell icon behavior remains stable and does not display contradictory state.
- User signs out from the drawer while it is open; navigation state resets cleanly and no authenticated-only actions remain visible.
- User role changes between sessions; admin button visibility reflects the currently restored session role at drawer open time.
- Current page is already the selected destination; selecting that menu item does not produce broken navigation behavior.
- User rapidly opens/closes the drawer repeatedly; state remains stable and does not duplicate or reorder menu rows.
- The screen behind the drawer remains partially visible but not interactable while the drawer is open.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST provide a dedicated mobile navigation entry control (hamburger icon) for phone and small-tablet layouts.
- **FR-002**: System MUST open a right-side navigation drawer when the hamburger icon is activated on phone and small-tablet layouts.
- **FR-003**: The drawer MUST cover about 90% of viewport width while leaving a narrow visible area of background content.
- **FR-004**: The visible background area behind the open drawer MUST be visually blurred.
- **FR-005**: The first drawer row MUST display the Longtail brand logo on the left and a notifications bell icon on the right.
- **FR-006**: The drawer MUST include the following rows in this exact top-to-bottom order after the first row: Account, Comparison, Search, Home, Sources, Datasets.
- **FR-007**: Each drawer row button MUST close the drawer immediately and navigate to its corresponding destination when selected.
- **FR-008**: The Comparison row MUST display the compared dataset counter using the same counting behavior and semantics as the existing top navigation comparison control.
- **FR-009**: The drawer bottom section MUST include a Sign out action that redirects users to the Home page in signed-out state.
- **FR-010**: The drawer bottom section MUST include an Admin action only for users with admin-eligible privilege.
- **FR-011**: The Admin action MUST appear above the Sign out action in the drawer bottom section.
- **FR-012**: Non-admin users MUST NOT see the Admin action in the drawer.
- **FR-013**: The notifications bell icon in the drawer header MUST preserve existing notification access behavior and unread-state consistency expectations.
- **FR-014**: The drawer experience MUST replace the current cluttered multi-row mobile top-nav pattern on phone and small-tablet layouts.
- **FR-015**: While the drawer is open, background content MUST not accept unintended interaction.
- **FR-016**: Drawer open and close behavior MUST remain stable under repeated user interactions.
- **FR-017**: The feature MUST preserve signed-in and signed-out navigation safety boundaries, including role-based action visibility.
- **FR-018**: The feature MUST include explicit behavior for comparison and notification zero/empty states without breaking drawer layout.
- **FR-019**: The mobile drawer MUST be available from all pages that use the shared site shell.
- **FR-020**: Existing desktop navigation behavior MUST remain unchanged outside the phone and small-tablet activation range.
- **FR-021**: When a signed-out user selects an auth-protected drawer action, the system MUST redirect the user to the Login page.
- **FR-022**: Drawer activation range MUST apply to viewport widths at or below 1024 CSS pixels and MUST remain disabled above 1024 CSS pixels.
- **FR-023**: Notification bell behavior in the drawer MUST preserve existing bell control semantics, including unread badge visibility and toggle/open-close behavior.

### Key Entities _(include if feature involves data)_

- **Mobile Navigation Drawer**: The small-screen navigation surface containing ordered navigation rows, top-row utility elements, and footer actions.
- **Drawer Menu Item**: A single user-visible drawer action row with a fixed position in the required order and a destination behavior.
- **Drawer Utility State**: The role- and session-driven state that controls visibility and values for notifications access, comparison counter, admin action, and sign-out behavior.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In usability validation on small screens, at least 95% of users can open the drawer and navigate to a requested destination in 2 interactions or fewer.
- **SC-002**: In visual acceptance checks across supported small-screen breakpoints, 100% of audited screens show the required drawer row order without multi-row top-nav clutter and with drawer width at about 90% of viewport width.
- **SC-003**: In role-based validation samples, 100% of admin users see the Admin action and 100% of non-admin users do not.
- **SC-004**: In comparison-state regression checks, 100% of audited drawer renders show a comparison counter value consistent with existing comparison selection state.
- **SC-005**: In sign-out flow validation, at least 99% of sign-out attempts triggered from the drawer complete successfully and land on the Home page in signed-out state.
- **SC-006**: In interaction-stability testing, drawer open/close and navigation actions complete without broken or duplicated menu state in 100% of audited repeated-interaction scenarios.
- **SC-007**: In responsive validation, drawer behavior activates for viewports <=1024px and remains inactive for viewports >1024px in 100% of audited checks.

## Assumptions

- The mobile drawer applies to phone and small-tablet layouts and does not change desktop navigation structure.
- Existing destination routes for Account, Comparison, Search, Home, Sources, Datasets, and Admin remain valid.
- Existing notification and comparison counter logic remains the source of truth and is reused in the drawer.
- Signed-out users can still open the mobile drawer, and selecting auth-protected actions redirects to the Login page.
- The brand row includes the existing Longtail logo treatment and existing notifications bell icon behavior.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code, and the
  full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before
  commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects, and can satisfy the commit-time coverage stop rule
  (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
- **CA-006 Configuration Integrity**: Any new service or pipeline component that requires
  credentials or external API keys will fail hard (exception/non-zero exit/job-level
  failure) when those variables are absent — no soft outcome recording, no silent
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source for
  any Docker Compose service that requires secrets. (N/A)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI
  components, Tailwind utilities, and shared abstractions in
  `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate
  one-off component patterns or new local CSS without a documented exception. (Yes)
