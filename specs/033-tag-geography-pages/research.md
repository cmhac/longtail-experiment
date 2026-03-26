# Research: Tag and Geography Discovery Pages

## Decision 1: Introduce dedicated topic and geography detail routes, but not list pages

- Decision: Add dedicated detail routes for one topic tag and one geography value, without adding top-level topic-directory or geography-directory pages in this feature.
- Rationale: The user request is specifically pill-driven navigation from existing dataset surfaces into one metadata-specific destination page. Detail routes satisfy that need without expanding scope into separate browse directories.
- Alternatives considered:
  - Add `/topics` and `/geographies` index pages now: rejected because the current request does not require standalone metadata inventories.
  - Reuse the existing dataset catalog with query params only: rejected because the user asked for dedicated detail pages opened by pill clicks.

## Decision 2: Reuse the existing source-detail vertical-slice pattern

- Decision: Model topic and geography browsing after the existing source discovery implementation by adding first-class backend query entrypoints, service methods, HTTP routes, frontend client methods, and frontend detail pages.
- Rationale: The repository already has a working pattern for entity-specific discovery pages that return one header context plus a dataset list. Reusing that shape reduces architectural drift.
- Alternatives considered:
  - Build metadata pages purely in the frontend by filtering catalog payloads: rejected because metadata pages need stable deep links, explicit not-found/error behavior, and backend-backed dataset membership guarantees.
  - Introduce a separate metadata-discovery service boundary: rejected because the current discovery service already owns catalog, source, and dataset detail reads.

## Decision 3: Use route-safe slugs derived from visible metadata labels

- Decision: Represent topic tags and geography values in routes with normalized, route-safe slugs derived from the current display labels, while returning the original display label in response payloads.
- Rationale: Existing UI surfaces expose topic and geography as human-readable strings. A derived slug keeps navigation stable and readable while preserving the original label for display.
- Alternatives considered:
  - Use raw labels directly in routes: rejected because punctuation, spacing, and case inconsistencies would create brittle URLs.
  - Expose internal database UUIDs for tags: rejected because current frontend metadata surfaces do not expose or require internal identifiers, and geography currently has no equivalent persisted discovery identifier.

## Decision 4: Keep geography browsing backed by the current discovery-facing geography label

- Decision: Geography detail pages will be driven by the current discovery-facing geography label rather than introducing hierarchy-aware geography membership in this feature.
- Rationale: The current discovery repository already persists and serves one `geographic_scope` label per dataset. That is sufficient for the requested “open a detail page with all datasets in that geography” behavior.
- Alternatives considered:
  - Re-model discovery around the existing taxonomy hierarchy tables now: rejected because current dataset discovery reads do not join to those tables and the feature request does not require hierarchical expansion or rollups.
  - Add a new geography join table immediately: rejected because it would add schema churn before exhausting the current dataset-level label approach.

## Decision 5: Reuse the existing dataset list presentation with linked pills

- Decision: Keep metadata detail pages visually aligned with source detail pages and dataset catalog rows by reusing the existing dataset list hierarchy and extending pill rendering to support links.
- Rationale: Dataset rows already contain the geography and topic signals that will power this feature. Turning those pills into navigable links preserves familiarity and keeps scope focused.
- Alternatives considered:
  - Introduce a bespoke card/grid layout for metadata pages: rejected because it would duplicate the browse hierarchy already used across catalog and source discovery surfaces.
  - Make only dataset-detail pills clickable and leave list-row pills static: rejected because the request explicitly covers “one of the pills” from current dataset surfaces broadly, and consistent behavior across list and detail contexts is easier to learn.

## Decision 6: Preserve current topic-tag normalization rules and add no new pipeline fields by default

- Decision: Keep the existing pipeline behavior where topic tags are normalized and persisted as stable tag names, and keep geography sourced from the current dataset geographic scope field unless implementation proves a new metadata field is necessary.
- Rationale: Topic tags already have normalized storage and discovery reads. Geography already flows through ingest into `data_series.geographic_scope`, which is enough for label-based membership pages.
- Alternatives considered:
  - Add dedicated ingest payload fields for route slugs: rejected because slugs can be derived consistently in the query layer.
  - Add immediate schema changes for geography normalization: rejected because the user request can be satisfied with current persisted data plus query-layer normalization.
