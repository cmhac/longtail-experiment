# Feature Specification: Unified Feed List Components

**Feature Branch**: `[039-unified-feed-list]`  
**Created**: 2026-03-30  
**Status**: Draft  
**Input**: User description: "Ok we're going to create a new component group for this. We should create several components for managing the entire feed and list ui we currently ahve. this includes the main card wrapping the feed, the optional title (e.g. "Recent Updates" on the home page), components for the row, the main title, subtitle, update date, and the text above that date which we will call the "display category". display category is flexible and could be anything that is needed to be dislpayed in that spot on the left above the date. Create a spec for this change"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Reuse One List Surface Pattern (Priority: P1)

As a product contributor, I can assemble feed and list surfaces from one shared group of presentation components so repeated discovery list layouts do not need to be rebuilt separately for each page.

**Why this priority**: The core value of this feature is consolidating a repeated UI pattern into one shared presentation system that can support current and future discovery surfaces.

**Independent Test**: Can be fully tested by rendering the home recent-updates section and a catalog-style list surface with the new component group and confirming both are composed from the same shared feed shell and row primitives while preserving their distinct surrounding page context.

**Acceptance Scenarios**:

1. **Given** a page needs a bordered list or feed surface, **When** it uses the shared feed wrapper component, **Then** the page receives the same base container treatment without rebuilding that shell locally.
2. **Given** a page needs a list section heading, **When** it uses the shared optional feed title area, **Then** the heading appears in the standard location above the rows and can also be omitted without breaking spacing or structure.
3. **Given** multiple discovery pages render list rows, **When** contributors compare the rendered structure, **Then** row layout, title hierarchy, left-side metadata placement, and supporting text all follow one reusable pattern.

---

### User Story 2 - Support Flexible Left-Side Metadata (Priority: P2)

As a product contributor, I can provide a flexible display category above the update date so the same row pattern can represent different types of list metadata without creating separate one-off row variants.

**Why this priority**: The left-side metadata rail is one of the main differences between existing list surfaces, so making it flexible is necessary for the shared component group to cover real use cases.

**Independent Test**: Can be fully tested by rendering rows with different display-category values, different dates, and missing optional text, then confirming the row still presents a stable hierarchy and readable metadata rail across each variant.

**Acceptance Scenarios**:

1. **Given** a row has a display-category value, **When** it renders, **Then** that value appears above the update date in the left-side metadata rail.
2. **Given** different surfaces need different display-category text, **When** they supply values such as source type, source name, or another label, **Then** the row presents each value without requiring a separate row component for each case.
3. **Given** a row omits optional supporting copy such as subtitle text, **When** it renders, **Then** the remaining title and metadata structure stays readable and visually stable.

---

### User Story 3 - Preserve Current Discovery Surface Behavior (Priority: P3)

As a visitor, I can continue using current feed and list experiences while the presentation is reorganized into shared components, so visual consistency improves without changing the surrounding page behavior I rely on.

**Why this priority**: Shared presentation only succeeds if existing discovery flows remain intact while moving to the new component group.

**Independent Test**: Can be fully tested by rendering the current home recent-updates feed and current dataset/source list surfaces after migration and confirming headings, links, empty states, and ordering remain intact while the new shared components are in use.

**Acceptance Scenarios**:

1. **Given** the home page recent-updates section is rendered, **When** it adopts the shared component group, **Then** it still shows its section title, row ordering, and link behavior expected for that surface.
2. **Given** a list surface does not need a section title, **When** it adopts the shared component group, **Then** the rows still render correctly without an empty heading placeholder.
3. **Given** current discovery list surfaces have existing empty or fallback states, **When** the shared component group is introduced, **Then** those states remain available and are not replaced by broken or partial list UI.

### Edge Cases

- What happens when a feed uses the shared wrapper but intentionally provides no section title? The wrapper preserves correct spacing and row alignment without rendering an empty heading block.
- What happens when the display-category text is unusually short, long, or absent? The metadata rail remains readable and the row does not collapse or overlap adjacent content.
- What happens when the update date is unavailable or malformed? The row continues to render safe fallback text rather than failing to display.
- What happens when subtitle content is absent? The row omits that line cleanly without leaving awkward gaps.
- What happens when a row contains long titles or long supporting text? The shared row layout preserves hierarchy and remains readable across supported viewport sizes.
- What happens when a surface needs the shared row layout but not the same feed heading used on the home page? The shared component group supports that surface without requiring a duplicate wrapper implementation.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST provide one shared feed or list wrapper component that defines the standard outer container for discovery list surfaces.
- **FR-002**: The shared wrapper MUST support an optional title region that can be rendered when a surface needs a visible section heading and omitted when it does not.
- **FR-003**: The system MUST provide a shared row component for list entries within the new component group.
- **FR-004**: The shared row component MUST provide dedicated presentation slots or props for a primary title, an optional subtitle, an update date, and a display-category value.
- **FR-005**: The display-category value MUST appear in the left-side metadata area above the update date whenever it is provided.
- **FR-006**: The display-category field MUST be flexible enough to support different labels across discovery surfaces without requiring separate row component families for each label type.
- **FR-007**: The system MUST provide shared title and metadata subcomponents or equivalent reusable presentation parts so feed and list surfaces can assemble the standard hierarchy without duplicating local markup.
- **FR-008**: The new component group MUST preserve the current readable hierarchy of metadata rail, title block, optional supporting text, and row-level supporting content across supported surfaces.
- **FR-009**: The new component group MUST support surfaces with a visible feed title and surfaces without one using the same shared foundation.
- **FR-010**: Existing discovery surfaces that migrate to the new component group MUST preserve their current item ordering, destinations, and surrounding page-level behavior.
- **FR-011**: Existing empty, unavailable, and error states outside the row wrapper scope MUST remain usable after surfaces adopt the new component group.
- **FR-012**: The shared component group MUST remain readable and structurally stable across supported desktop and mobile viewport ranges.
- **FR-013**: The system MUST allow current list and feed surfaces to adopt the new shared presentation group without introducing new one-off duplicate row or wrapper patterns for the same hierarchy.
- **FR-014**: The feature MUST include regression coverage for the shared wrapper, optional title region, row hierarchy, flexible display-category behavior, and the migrated discovery surfaces that consume them.

### Key Entities _(include if feature involves data)_

- **Feed/List Wrapper**: The shared outer presentation shell for discovery feeds and list surfaces, including container spacing and optional heading treatment.
- **Feed/List Title Region**: The optional heading area used for surfaces such as home recent updates that need a visible section title above the rows.
- **Shared List Row**: The reusable entry presentation unit containing the metadata rail and content body for one item.
- **Display Category**: The flexible metadata label shown above the update date in the left-side rail and intended to accommodate different surface-specific contexts.
- **Row Text Hierarchy**: The structured set of title, optional subtitle, update date, display category, and any supporting row text needed to preserve consistent readability.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In design and implementation review, 100% of migrated discovery feed/list surfaces use the shared wrapper and row component group rather than separate duplicated container and row structures.
- **SC-002**: In regression validation, 100% of audited migrated surfaces preserve their expected heading visibility, row ordering, and navigation outcomes after adopting the shared component group.
- **SC-003**: In responsive QA across agreed desktop and mobile viewport samples, 100% of audited rows preserve readable left-side metadata, title hierarchy, and supporting text with no overlap or clipped content.
- **SC-004**: In usage validation, contributors can assemble a titled feed surface and an untitled list surface from the same shared component group without creating new duplicate list-specific primitives.

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
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source
  for any Docker Compose service that requires secrets. (N/A)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI
  components, Tailwind utilities, and shared abstractions in
  `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate
  one-off component patterns or new local CSS without a documented exception.
  (Yes)

## Assumptions

- The feature is limited to shared presentation structure and does not require new end-user workflows beyond current feed and list behavior.
- Existing discovery surfaces may retain their current page-specific empty, error, filtering, and pagination behavior while adopting the new component group.
- The shared row pattern continues to support optional supporting text rather than requiring every surface to show both a title and subtitle.
- The display category is a presentation field and not a new business taxonomy or filtering dimension.
- Current link destinations and ordering semantics remain the source of truth for migrated surfaces unless changed by a separate feature.
