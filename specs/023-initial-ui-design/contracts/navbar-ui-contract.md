# Contract: Initial Navbar UI Behavior

## Interface Summary

- Interface type: Frontend shell UI contract
- Consumer: Home page users, frontend integration/contract tests
- Provider: `apps/frontend/src/shell/site-header.tsx` and related shell/theme styles

## Structural Contract

The home page shell must render a semantic top header region containing exactly three areas:

1. Brand area (left)
2. Primary tab area (center/left-center)
3. Utility icon area (right)

### Required visible labels and controls

- Brand text: `Longtail` (serif-styled treatment)
- Tabs: `Home`, `Datasets`, `Trends`
- Utility icons: search icon control, profile icon control

### Required test and accessibility hooks

- Header region test id: `shell-header`
- Navbar container test id: `navbar-container`
- Brand link test id: `navbar-brand-link`
- Tab test ids: `navbar-tab-home`, `navbar-tab-datasets`, `navbar-tab-trends`
- Utility test ids: `navbar-search-control`, `navbar-profile-control`
- Profile dropdown test id (when open): `navbar-profile-dropdown`
- Navbar semantic landmark: `nav[aria-label="Primary"]`
- Profile toggle must expose `aria-expanded` and `aria-controls`.

### Required state defaults

- Home tab: enabled and active
- Datasets tab: disabled
- Trends tab: disabled
- Search icon: disabled
- Profile icon: enabled

## Interaction Contract

### Homepage navigation

- Clicking the brand label routes to homepage (`/`).
- Clicking Home tab routes to homepage (`/`).

### Disabled controls

- Clicking Datasets or Trends does not navigate.
- Clicking search does not trigger search behavior.
- Repeated clicks on disabled controls preserve disabled state and do not introduce side effects.
- Datasets, Trends, and search controls expose disabled state (`disabled` + `aria-disabled` for disabled tabs).

### Profile dropdown

- Clicking profile icon toggles a small anchored dropdown panel.
- Dropdown content is exactly one placeholder message: `dropdown coming soon`.
- No additional actionable menu items are rendered in this feature.
- Repeated profile clicks toggle open/close without duplicated overlays.

## Appearance and Responsiveness Contract

- Navbar spans full available page width.
- Navbar and dropdown remain readable in both light and dark appearance modes.
- On narrow viewport widths, controls remain visible without overlapping in a way that obscures required labels/icons.

## Test Assertions (Minimum)

1. Structural test verifies header region, required labels, and required icon controls.
2. Interaction test verifies brand/Home navigate to `/`.
3. Interaction test verifies Datasets/Trends/search remain disabled and inert.
4. Interaction test verifies profile dropdown opens with exactly `dropdown coming soon` content.
5. Visual/state test verifies light and dark mode readability baseline.
6. Contract test verifies expected test ids and semantic navbar landmark are present.

## Versioning

- Contract version: 1.0
- Backward compatibility note: Additional profile dropdown actions are a future contract revision and must update this document, spec artifacts, and tests in the same change.
