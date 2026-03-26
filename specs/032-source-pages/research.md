# Research: Source Discovery Pages

## Decision 1: Add first-class source routes and HTTP contracts instead of reusing grouped catalog payloads in-place

- Decision: Introduce dedicated source list and source detail routes in the frontend and matching source list/detail query entrypoints in the backend.
- Rationale: The existing dataset catalog `groups` projection is optional metadata on a dataset response and does not provide a complete source-detail payload or route-level failure semantics. First-class source contracts make list/detail navigation explicit and testable.
- Alternatives considered:
  - Reuse `/api/datasets?group_by_source=true` as the only source surface: rejected because it does not provide a dedicated source detail payload and would force the frontend to reconstruct source pages from dataset-first responses.
  - Keep source browsing entirely client-side from the full dataset catalog: rejected because it scales poorly, hides source-specific not-found behavior, and leaves the backend without an explicit source contract.

## Decision 2: Use the existing discovery source identifier model derived from source display names for this feature

- Decision: Treat the current discovery-facing `source.id` projection, derived from normalized source display names, as the route-safe source identifier for source pages in this feature.
- Rationale: Existing dataset payloads already expose this identifier shape, and the repository currently derives it deterministically from persisted source names. Reusing that model keeps the feature compatible with current persisted data and avoids unnecessary schema churn.
- Alternatives considered:
  - Introduce a new persisted source slug column or expose database UUIDs: rejected because it expands migration and compatibility scope beyond the immediate user-facing need.
  - Use pipeline runtime `source_key` values as route ids: rejected because runtime source keys and discovery source names are not currently one-to-one and would misalign with existing discovery responses.

## Decision 3: Keep pipeline storage behavior unchanged and document its impact on source identity

- Decision: Do not add new pipeline write-path behavior for this feature; rely on the current persistence of `source_name` and `source_type` into `source_profiles`, with source browsing built on top of that model.
- Rationale: Source list/detail pages read from existing persisted metadata, and pipeline already upserts source attribution for every dataset. The primary need is contract clarity, not a new ingestion capability.
- Alternatives considered:
  - Add new pipeline metadata fields solely for frontend source pages: rejected because current persistence already contains the source attribution required for discovery.
  - Treat pipeline as out of scope and leave source identity undocumented: rejected because source browsing depends on understanding how source attribution is written into persistence.

## Decision 4: Reuse the existing dataset row presentation for source detail dataset listings

- Decision: Render source-owned datasets using the existing unified dataset row/list hierarchy already used by the dataset catalog and recent updates feed.
- Rationale: Source detail pages need to present a filtered dataset list, not invent a new dataset presentation pattern. Reuse preserves scannability and reduces visual drift.
- Alternatives considered:
  - Create a new source-detail-specific dataset card design: rejected because it adds visual divergence without changing the underlying user task.
  - Show only dataset titles as plain links: rejected because it removes summary context that users rely on when browsing the catalog.

## Decision 5: Keep source fallback behavior aligned with current discovery patterns

- Decision: Implement source list/detail empty states, generic error states, and source not-found handling using the same discovery fallback conventions already used for dataset pages.
- Rationale: Consistent fallback semantics reduce user surprise and simplify testing across discovery routes.
- Alternatives considered:
  - Introduce custom full-screen failure treatments just for source pages: rejected because they would diverge from current shell behavior and add unnecessary UX scope.
  - Redirect unknown sources back to the list page silently: rejected because it hides invalid-link states and makes debugging stale links harder.
