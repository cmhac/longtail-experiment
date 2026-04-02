# Research: Current-State Multi-Lookback Trends

## Decision 1: Treat this revision as a read-model and UI refinement, not a new trend-processing redesign

- Decision: Keep the existing multi-lookback persistence and canonical descriptor computation model as the implementation baseline, and plan only the incremental work needed to expose and render that descriptor on list surfaces plus the revised detail heading.
- Rationale: The repository already contains canonical descriptor persistence, dataset-detail descriptor reads, and frontend detail/chart simplification work. The changed scope is now about propagating the current-trend descriptor to dataset-summary responses and replacing the removed chip with a shared arrow indicator.
- Alternatives considered:
  - Re-plan the entire feature from raw pipeline persistence through UI again: rejected because it no longer matches repository reality and would create stale planning guidance.
  - Reintroduce lifecycle-span or overlay behavior as part of this revision: rejected because the updated spec explicitly keeps overlay removal and canonical current-state rendering.

## Decision 2: Use one shared canonical descriptor shape for both dataset-summary and dataset-detail rendering

- Decision: Reuse the canonical descriptor as the single render-ready trend payload for both dataset-summary rows and dataset-detail rendering, with no separate lightweight list-only trend schema.
- Rationale: One shared shape keeps client rendering simple, preserves deterministic server ownership, and avoids drift between list/detail interpretations of the same current-trend state.
- Alternatives considered:
  - Add a separate list-only trend enum or display token: rejected because it duplicates semantics already present in the canonical descriptor.
  - Compute list display state client-side from lookback snapshots: rejected because the spec forbids client-side weighting or ranking logic.

## Decision 3: Extend `DatasetSummary`-based contracts rather than inventing list-specific endpoint variants

- Decision: Add canonical current-trend descriptor data to the common dataset-summary contract used by catalog, search, source, topic, geography, and recent dataset update surfaces.
- Rationale: The backend and frontend already centralize dataset-row behavior around `DatasetSummary` and `UnifiedDatasetRow`. Updating the shared contract keeps every dataset-list surface aligned and avoids one-off endpoint behavior.
- Alternatives considered:
  - Patch only homepage recent updates: rejected because the spec requires all dataset list components.
  - Introduce dedicated list endpoint variants for trend-enabled rows: rejected because it fragments the read model and duplicates integration work.

## Decision 4: The frontend should render one shared arrow indicator primitive in both list and detail contexts

- Decision: Build one shared trend-indicator component in `apps/frontend/src/components` and consume it from the dataset-row and dataset-detail heading seams.
- Rationale: The updated UX uses the same semantic mapping in two places. A shared primitive satisfies the constitution requirement to extend reusable abstractions for repeated UI patterns.
- Alternatives considered:
  - Inline separate SVG/class logic in dataset rows and detail heading: rejected because it duplicates visual mapping and increases drift risk.
  - Keep a text chip on detail while adding arrows to lists: rejected because the spec now standardizes on the arrow indicator.

## Decision 5: Map arrow state directly from canonical descriptor direction and strength

- Decision: Use canonical `direction` plus `strength` to derive exactly four render states: straight-up green, up-right green, down-right red, and straight-down red; descriptors without a usable render state fall into an explicit unavailable state.
- Rationale: This preserves server-side trend selection while keeping the view model deterministic and minimal.
- Alternatives considered:
  - Introduce a new persisted icon state in storage: rejected because the canonical descriptor already carries the required semantic dimensions.
  - Infer strong vs mild from `trend_label` text parsing only: rejected because `strength` exists as the cleaner, more stable signal.

## Decision 6: Query-time summary projection should join the latest canonical descriptor once per dataset row

- Decision: Backend dataset-summary queries should project the latest canonical descriptor as part of their existing summary row assembly, rather than requiring a secondary fetch per row.
- Rationale: The spec requires list surfaces to render current trend directly, and per-row follow-up queries would add avoidable complexity and latency.
- Alternatives considered:
  - Fetch detail payloads per list row: rejected because it is heavier, duplicates data, and breaks the shared summary contract shape.
  - Omit unavailable descriptors from summaries: rejected because the spec requires explicit unavailable states instead of omission.

## Decision 7: Preserve dataset-detail lookback snapshots as diagnostics while shifting primary UI emphasis to the heading indicator

- Decision: Keep the dataset-detail response contract exposing both canonical descriptor and lookback snapshots, while the visible primary current-trend UI becomes the arrow indicator next to `Historical Trend`.
- Rationale: The lookback data remains useful for auditability and diagnostics, but the user-facing current trend should now be expressed through the simpler indicator.
- Alternatives considered:
  - Remove lookback snapshots from detail responses: rejected because the broader feature still requires explicit lookback-state exposure.
  - Move the indicator back under the page title: rejected because the revised spec and provided screenshot place it by the chart heading.

## Repository Seams Confirmed For This Revision

- Backend shared summary contract currently lives in `apps/backend/src/contract/query/dataset_search_query.py` and is reused by catalog, search, and metadata-discovery responses.
- Recent dataset updates extend that same summary shape in `apps/backend/src/contract/query/dataset_recent_updates_query.py`.
- Dataset-detail canonical descriptor validation already exists in `apps/backend/src/contract/query/dataset_detail_query.py`.
- Persisted canonical descriptor reads already exist in `apps/backend/src/query/dataset_discovery_persisted_repository.py` and are wired into detail assembly in `apps/backend/src/query/dataset_discovery_service.py`.
- Shared dataset-row rendering currently centers on `apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx` and mapper helpers in `apps/frontend/src/components/discovery/unified-dataset-row-mappers.ts`.
- The detail heading seam currently lives in `apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx`.

## Planning Outcome

- All previously unresolved technical questions for this revision are closed.
- No `NEEDS CLARIFICATION` markers remain for planning.
- The implementation plan can proceed directly to data-model, contract, and task breakdown updates for summary payload expansion and shared arrow-indicator rendering.

## Phase 6 Revision Execution Notes

- Revised scope confirmation: dataset-summary payloads and dataset-detail payloads both expose canonical trend descriptor fields required for direct rendering.
- Shared indicator confirmation: one directional indicator primitive is the only current-trend UI state shown in dataset rows and by the `Historical Trend` heading.
- Client responsibility confirmation: frontend only maps API descriptor fields into visual indicator states; no client-side weighting or lookback ranking is permitted.
