# UI Standardization Contract

## Purpose

Define the contract for the `036-heroui-ui-migration` feature so implementation and review can determine:

- which frontend surfaces are in scope
- what standardized pattern is expected for each surface type
- which parts of the current Longtail identity must be preserved
- when a retained exception is acceptable

## In-Scope Routes

- `/`
- `/search`
- `/datasets`
- `/datasets/[id]`
- `/sources`
- `/sources/[sourceId]`
- `/topics/[topicId]`
- `/geographies/[geographyId]`

## In-Scope Shared Surface Categories

### 1. Shell Surfaces

- Root layout wrapper
- Header and navigation
- Footer
- Shared constrained-content wrappers

### 2. Search and Filter Surfaces

- Homepage search hero
- Navbar search expansion
- Dataset list filter and sort controls
- Shared popover/listbox suggestion surfaces

### 3. Content and Listing Surfaces

- Dataset rows
- Dataset cards
- Source rows/lists
- Recent updates feed
- Paginated or infinite-load list containers

### 4. State Surfaces

- Empty states
- Error states
- Unavailable and no-results surfaces

### 5. Detail and Metadata Surfaces

- Dataset detail header and analysis sections
- Source detail header
- Topic detail header
- Geography detail header
- Chart and table container surfaces

## Standardization Rules

### Rule 1: Prefer approved HeroUI primitives and composition

When an in-scope surface has a suitable HeroUI pattern, implementation must prefer HeroUI primitives and composition over custom raw HTML wrappers.

Examples:

- input-like controls should use HeroUI input/combo-box style surfaces
- button-like actions should use HeroUI button primitives or HeroUI button styling patterns
- shared containers should use HeroUI surface/card-style patterns where practical

### Rule 2: Prefer shared Tailwind utility layout over bespoke page CSS

Spacing, grouping, alignment, and width behavior should be expressed through shared utility classes or shared component composition before introducing new page-specific CSS.

### Rule 3: Preserve protected identity guardrails

The migration must preserve:

- Longtail typography families and tone
- Longtail color intent and recognizable shell contrast
- recognizable navigation and page-orientation cues

### Rule 4: Preserve behavior before visual cleanup

Search, filtering, browsing, navigation, and detail-page reading flows must remain functionally unchanged unless a change is explicitly added to scope later.

### Rule 5: Standardize repeated surfaces once, then reuse them

If the same interface need appears on multiple routes, the migration must converge on one shared standardized pattern rather than creating route-local replacements.

### Rule 6: Route pages must use the shared shell frame

Route pages in scope must compose the shared shell through `apps/frontend/src/shell/site-page-frame.tsx` unless a route has a documented reason to diverge. Header, constrained-content main region, and optional footer rendering should not be hand-recreated per page.

### Rule 7: Repeated list and state surfaces must render through HeroUI cards

Shared content surfaces such as dataset rows, recent-updates feeds, catalog containers, search result containers, detail headers, and explicit state messages must present through HeroUI card-style surfaces plus Tailwind utility layout. Bare section or paragraph wrappers are not the default approved pattern for those surfaces.

## Allowed Exception Policy

A retained non-standard surface is allowed only when at least one of the following is true:

- it preserves protected brand identity that would be materially degraded by standardization
- it preserves product clarity for data-dense analytical content
- there is no suitable standardized equivalent without causing a user-facing regression

Each allowed exception must include:

- the surface name
- the file or route location
- the reason it remains custom
- what standardized alternatives were considered

## Approved Exceptions

### Exception 1: Chart internals remain custom

- Surface: Recharts visualization internals
- Location: `apps/frontend/src/components/discovery/ObservationsChart.tsx`
- Reason: Chart rendering relies on Recharts primitives and density-specific markup that HeroUI does not replace directly without loss of clarity.
- Alternatives considered: wrapping the chart in fully custom card markup, or replacing chart internals with HeroUI-only structure

### Exception 2: Data table internals remain custom

- Surface: observations table markup
- Location: `apps/frontend/src/components/discovery/ObservationsTable.tsx`
- Reason: The table needs dense, semantic tabular markup and sorting/readability control that is clearer when kept as table-first HTML.
- Alternatives considered: replacing the table body with card/list patterns or introducing heavier abstraction around table cells

### Exception 3: Typography and shell identity tokens remain custom variables

- Surface: shell typography and Longtail monochrome token definitions
- Location: `apps/frontend/src/app/globals.css`, `apps/frontend/src/theme/monochrome-theme.ts`, `apps/frontend/src/theme/theme-preference.ts`
- Reason: The feature explicitly preserves Longtail identity; HeroUI defaults are used structurally, while typography and color intent remain governed by app-level variables.
- Alternatives considered: adopting HeroUI default typography and color variables wholesale

## Validation Requirements

### Automated validation

- Affected frontend tests must be updated for changed DOM semantics and interaction paths.
- Shared-shell, route, and control tests must continue covering user-visible workflows.

### Manual validation

- Review all in-scope routes at desktop and mobile widths.
- Confirm preserved typography and color identity.
- Confirm empty/error/loading surfaces remain explicit.
- Confirm no undocumented retained legacy pattern remains in the audited scope.

## Completion Criteria

This feature is complete when:

1. every in-scope shared surface is migrated or explicitly documented as an exception
2. primary discovery workflows remain behaviorally stable
3. preserved identity guardrails remain visible
4. automated tests and manual validation pass
