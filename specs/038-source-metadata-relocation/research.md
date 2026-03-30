# Research: Source Metadata and Adapter Relocation

## Decision 1: Move maintained adapters to a single new top-level source package

- Decision: Relocate maintained adapter modules from `apps/pipeline/src/orchestration/jobs/sources` to `apps/pipeline/src/sources` and update discovery, bootstrap generation, schedules, Dagit asset derivation, and tests to treat the new package as the sole maintained adapter surface.
- Rationale: The user goal is easier discoverability for contributors. A single canonical source package delivers that benefit clearly and avoids long-term ambiguity about where new adapters belong.
- Alternatives considered:
  - Keep both directories active and scan both: rejected because it prolongs ambiguity, complicates collision detection, and weakens the onboarding improvement.
  - Add re-export shims in the old directory indefinitely: rejected because it preserves deep-path maintenance burden and increases discovery complexity.

## Decision 2: Extend `SOURCE_SPEC` with required `title` and `description`

- Decision: Add required non-empty `title` and `description` fields to every source manifest and to the internal `SourceBuilderSpec` representation, with startup validation and bootstrap generation enforcing both.
- Rationale: The metadata is manifest-owned and source-level by definition, so `SOURCE_SPEC` is the authoritative place to require it. Fail-fast validation prevents blank or partial source metadata from leaking into persistence and UI.
- Alternatives considered:
  - Infer source title from `source_key` and keep description optional: rejected because the feature explicitly requires human-readable metadata and no longer wants key-derived labels as the primary display form.
  - Store metadata only in docs or frontend mappings: rejected because it would create drift between onboarding, persistence, APIs, and runtime discovery.

## Decision 3: Persist source metadata in `source_profiles` with stable `source_key`

- Decision: Expand `source_profiles` so source-level rows carry stable `source_key`, source title, and source description, then upsert source profiles by `source_key` while continuing to preserve source attribution required by dataset membership and observation ownership.
- Rationale: Source metadata belongs at the source level, not repeated across datasets. Persisting it in `source_profiles` gives backend source queries a first-class authoritative record and allows future source-level experiences to rely on stable identity instead of reconstructed display names.
- Alternatives considered:
  - Continue grouping sources by `source_name` only: rejected because source identity would remain coupled to a display string and would not satisfy the requirement for source-spec-owned title/description.
  - Duplicate source title and description onto every dataset row only: rejected because it creates unnecessary duplication and makes source-level updates harder to keep consistent.

## Decision 4: Use `source_key` as the stable source identifier in backend and frontend source discovery flows

- Decision: Standardize source list/detail identifiers on persisted `source_key`, while exposing source title as the human-readable label and description as source context.
- Rationale: This aligns source browsing with the repository’s existing stable machine identity and avoids display-name-derived route identifiers. It also cleanly separates user-facing titles from identity, which the feature explicitly requires.
- Alternatives considered:
  - Keep slugified source-name identifiers for routes: rejected because route identity would still be derived from display text and could drift when titles change.
  - Expose database UUIDs as source identifiers: rejected because they are stable but not contributor-friendly or meaningful for route/debugging workflows.

## Decision 5: Carry source metadata through the pipeline persistence path as explicit source-level context

- Decision: Update the pipeline persistence flow so source-level metadata from the discovered manifest is available when canonical observations are persisted, rather than attempting to infer source title and description from dataset payload fields.
- Rationale: Adapter manifests already own source-level metadata. Passing that context into persistence keeps source title/description authoritative and avoids reconstructing source records from dataset-oriented observation fields.
- Alternatives considered:
  - Derive source metadata from the first dataset row written by each source: rejected because source-level information should not depend on one dataset’s payload completeness.
  - Add a separate post-ingest reconciliation job to fill source metadata: rejected because it delays correctness and complicates local reasoning about source state.

## Decision 6: Make bootstrap tooling and onboarding materials require the new metadata immediately

- Decision: Update the bootstrap CLI template, validation rules, generated scaffold, onboarding runbook, and onboarding skill to require source title and description as part of the standard adapter creation flow.
- Rationale: The repo already treats bootstrap-first onboarding as the standard. Making the new fields mandatory there keeps the developer experience consistent and prevents regressions from manual omissions.
- Alternatives considered:
  - Add the fields later during manual adapter completion: rejected because it weakens enforcement and makes scaffolded adapters incomplete by default.
  - Allow the fields to be optional for legacy adapters only: rejected because the feature assumes all maintained adapters are migrated in the same rollout so validation can become universal immediately.
