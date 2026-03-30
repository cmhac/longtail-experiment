# Data Model: Unified Feed List Components

## Overview

This feature does not introduce new persisted entities or backend contracts. The data model for planning purposes describes the frontend presentation entities that the new shared component group will accept and render.

## Entities

### Feed/List Surface

- Purpose: Represents one rendered discovery feed or list section that contains zero or more rows and may optionally include a visible section title.
- Fields:
  - `surfaceId`: stable test or consumer identity for the rendered list shell
  - `title`: optional visible heading text for titled surfaces
  - `rows`: ordered collection of row view models
  - `hasTitle`: derived state indicating whether a title region should render
  - `wrapperStyleVariant`: presentation variant within the shared shell contract
- Relationships:
  - Owns many `Feed/List Row` entities
- Validation rules:
  - Row order must be supplied by the consumer and preserved by the wrapper
  - Omitting `title` must not break wrapper spacing or structure

### Feed/List Row

- Purpose: Represents one reusable row inside the shared feed/list system.
- Fields:
  - `rowId`: stable identity for rendering and testing
  - `destinationHref`: optional or required navigational destination depending on consuming surface
  - `displayCategory`: flexible left-rail top-line metadata label
  - `updateDateText`: left-rail date or fallback date text
  - `title`: primary row heading
  - `subtitle`: optional supporting copy under the title
  - `supportingContent`: optional additional content such as pills or metadata chips
  - `interactionMode`: consumer-owned navigation behavior such as row-wide or title-only linking
- Relationships:
  - Belongs to one `Feed/List Surface`
  - Composes one `Row Metadata Rail`
  - Composes one `Row Content Body`
- Validation rules:
  - `title` is required
  - `displayCategory` may be omitted, but the metadata rail must remain structurally stable
  - `subtitle` may be omitted without leaving broken spacing
  - `updateDateText` must accept preformatted fallback text

### Row Metadata Rail

- Purpose: Represents the reusable left-side metadata stack shown beside the row body.
- Fields:
  - `displayCategory`
  - `updateDateText`
  - `layoutMode`: desktop stacked or mobile inline/collapsed presentation
- Relationships:
  - Belongs to one `Feed/List Row`
- Validation rules:
  - If `displayCategory` is present, it renders above `updateDateText`
  - Long labels must wrap or truncate safely within the established responsive layout rules

### Row Content Body

- Purpose: Represents the main content area of a feed/list row.
- Fields:
  - `title`
  - `subtitle`
  - `supportingContent`
- Relationships:
  - Belongs to one `Feed/List Row`
- Validation rules:
  - `title` remains the primary heading
  - `subtitle` is optional
  - Supporting content must not displace the title hierarchy or collapse body spacing

## Existing Source Data Mappings

### Dataset Surface Mapping

- Source inputs:
  - `DatasetSummary`
  - `DatasetRecentItem`
- Current mapped presentation fields:
  - `displayCategory`: current source label, currently derived from `source.name`
  - `updateDateText`: formatted `latest_update_at`
  - `title`: dataset title
  - `subtitle`: summary or normalized description text
  - `supportingContent`: geography and topic pills

### Source Surface Mapping

- Source inputs:
  - `SourceSummary`
- Current mapped presentation fields:
  - `displayCategory`: source type or fallback source label
  - `updateDateText`: formatted dataset-count text
  - `title`: source title
  - `subtitle`: description or generated browse summary
  - `supportingContent`: none in current source rows

## State and Transition Notes

- This feature does not change server-state transitions, pagination semantics, or API state machines.
- Populated-state rendering transitions remain owned by existing feed/list consumers.
- Empty, unavailable, and error-state transitions stay outside the shared component group and continue to use current page- or surface-level wrappers.
