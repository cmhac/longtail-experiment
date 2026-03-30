# UI Contract: Discovery Feed/List Component Group

## Purpose

Define the technical contract for the shared discovery feed/list component group that will replace repeated list wrapper and row markup across current discovery surfaces.

## Scope

This contract applies to the shared frontend component group used by:

- home recent updates
- dataset catalog list
- source catalog list
- dataset list surfaces embedded in source detail pages
- dataset list surfaces embedded in topic detail pages
- dataset list surfaces embedded in geography detail pages

This contract does not replace:

- page-level empty, unavailable, or error-state ownership
- backend or API payload contracts
- infinite-scroll sentinel/loading/error behavior outside the populated list wrapper

## Component Group Contract

The shared component group MUST expose reusable primitives that cover these roles:

1. Feed/list outer wrapper
2. Optional feed/list title region
3. Shared row container
4. Row metadata rail
5. Display-category text
6. Update-date text
7. Row title
8. Optional row subtitle

The component group MAY expose these as grouped named exports from one module.

## Composition Rules

### Wrapper

- MUST render the standard outer container for a populated feed/list surface.
- MUST support surfaces with a visible title region and surfaces without one.
- MUST preserve row order provided by the consuming surface.

### Title Region

- MUST be optional.
- MUST support the current home recent-updates heading pattern.
- MUST not leave empty vertical space when omitted.

### Row

- MUST preserve the current two-area hierarchy:
  - left metadata rail
  - right content body
- MUST support current responsive collapse behavior used by existing rows.
- MUST allow consuming surfaces to preserve current navigation semantics, including title-only link and row-wide link behavior.

### Metadata Rail

- MUST render `displayCategory` above `updateDateText` when both are provided.
- MUST remain stable if `displayCategory` is omitted.
- MUST accept already formatted display text from the consumer.

### Content Body

- MUST render `title` as the primary heading.
- MUST support optional `subtitle`.
- MUST support optional supporting row content after the title/subtitle block.

## Consumer Responsibilities

Consumers of the shared component group remain responsible for:

- shaping source payloads into the shared row contract
- formatting dates and fallback text
- deciding whether a surface uses title-only or row-wide linking
- rendering page-level empty, unavailable, and error states
- preserving current list ordering semantics

## Backward-Compatibility Requirements

- Existing surface-level test IDs for populated list wrappers SHOULD be preserved unless the migration explicitly introduces compatibility wrappers that retain equivalent test coverage.
- Current populated list surfaces MUST continue to render:
  - home recent updates heading and five-item cap
  - dataset catalog flat list
  - source catalog list
  - source/topic/geography detail dataset lists through the existing infinite-catalog flow
- Current link destinations and row ordering MUST remain unchanged.

## Verification Expectations

Implementation is complete only when tests verify:

- titled and untitled wrapper rendering
- display-category rendering above update-date text
- subtitle omission without broken spacing
- dataset row behavior after migration
- source row behavior after migration
- page-level regression behavior for home, datasets, and source list/detail surfaces
