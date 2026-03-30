# Implementation Plan: Source Metadata and Adapter Relocation

**Branch**: `[038-source-metadata-relocation]` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/038-source-metadata-relocation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Move maintained pipeline source adapters into a shallower top-level source package and introduce required source-level title and description metadata owned by each adapter manifest. The plan preserves `source_key` as the stable machine identity, extends dynamic discovery and bootstrap generation to require the new metadata, adds source-level persistence in `source_profiles`, updates backend source discovery contracts to expose human-readable source metadata, and refreshes frontend source surfaces to render source titles and descriptions instead of key-like labels.

## Technical Context

**Language/Version**: Python 3.12 for pipeline/backend layers; TypeScript 5.x + React 19 + Next.js 15 App Router for frontend  
**Primary Dependencies**: SQLAlchemy 2.x, Alembic, Pydantic 2.x, Dagster 1.x, existing pipeline source discovery/registration utilities, existing backend discovery service/repository contracts, HeroUI 3, Tailwind, existing frontend discovery client/types  
**Storage**: PostgreSQL 16 discovery metadata in `source_profiles`, `data_series`, `topic_tags`, and `observations`, with Alembic-managed schema changes required for source-level metadata  
**Testing**: pytest contract/integration/unit coverage for pipeline and backend, Vitest page/component/client coverage for frontend, Nx monorepo quality gates, pre-commit, mandatory full-suite test and coverage stop gates  
**Target Platform**: Local Docker Compose-backed ingest/discovery stack plus responsive web frontend in the existing discovery shell  
**Project Type**: Full-stack Nx monorepo vertical slice spanning pipeline adapter discovery, canonical persistence, backend discovery APIs, and frontend discovery routes  
**Performance Goals**: Preserve current adapter discovery startup characteristics and source list/detail responsiveness for dozens of sources and hundreds to low thousands of datasets without introducing noticeably slower browsing than current source pages  
**Constraints**: Preserve `source_key` as stable scheduling and traceability identity; migrate all maintained adapters in one rollout so fail-fast validation can become mandatory immediately; avoid one-off compatibility shims that keep both adapter locations active indefinitely; keep frontend work within existing HeroUI/Tailwind/shared-component patterns; full monorepo tests and coverage must pass before commit  
**Scale/Scope**: `apps/pipeline` source package and bootstrap tooling, `libs/db` schema/models, backend source discovery query contracts and repository projections, frontend source routes/components/types, provider onboarding docs and skill guidance, plus existing maintained adapter modules and their tests

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include
  cross-layer contract updates for vertical-slice changes?
- Quality gate enforcement: Are lint, format, type-check, and test gates defined with no
  suppression, bypass, or workaround strategy?
- Full-suite stop rule: Does the plan require `pnpm exec nx run-many -t test --all` to
  pass before any commit and before any AI agent ends work, with no exceptions?
- Coverage stop rule: Does the plan require `pnpm exec nx run-many -t coverage --all`
  to pass before any commit with >= 90% thresholds for every project?
- Test and coverage discipline: Does the plan include automated tests needed to maintain
  > = 90% coverage across affected backend/frontend projects?
- Local-first parity: Can the complete impacted flow run locally via unified Docker
  Compose, and are compose/healthcheck updates identified?
- Data integrity and reliability: Are data provenance, schema/contract versioning, and
  trend/alert regression protections explicitly designed?
- Configuration integrity: Do all new services/pipeline components fail hard on missing
  env vars/credentials (no soft outcomes), and is `docker/compose/local.secrets.env`
  declared as an `env_file` source for any service that requires secrets?
- Frontend UI consistency: For frontend changes, does the plan use HeroUI components,
  Tailwind utilities, and shared abstractions in `apps/frontend/src/components` for
  repeated patterns instead of new ad hoc CSS or duplicated markup?
- Documentation fidelity: Does the plan identify all documentation that MUST be added or
  updated for the proposed code and behavior changes?

Initial gate assessment:

- Monorepo cohesion: PASS. The change is explicitly a vertical slice across pipeline, persistence, backend, and frontend with updated contracts and docs in one feature.
- Quality gate enforcement: PASS. The plan keeps existing lint, format, type-check, test, duplication, and pre-commit gates intact.
- Full-suite stop rule: PASS. `pnpm exec nx run-many -t test --all` remains mandatory before commit and before any handoff.
- Coverage stop rule: PASS. `pnpm exec nx run-many -t coverage --all` remains mandatory before commit.
- Test and coverage discipline: PASS. The plan adds pipeline manifest/bootstrap tests, DB migration/model coverage, backend contract/query coverage, and frontend page/component/client coverage.
- Local-first parity: PASS. The feature stays within the current local compose stack; manual validation will run against the restarted stack after migration and ingest.
- Data integrity and reliability: PASS. The plan makes source-level metadata manifest-owned, keeps `source_key` stable, defines migration/backfill behavior, and updates source list/detail contracts accordingly.
- Configuration integrity: PASS. No new credentialed integrations or secret requirements are introduced.
- Frontend UI consistency: PASS. Frontend work remains within existing source pages and shared discovery components.
- Documentation fidelity: PASS. The plan includes runbooks, skill guidance, spec artifacts, and AGENTS review for workflow/path changes.

## Project Structure

### Documentation (this feature)

```text
specs/038-source-metadata-relocation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── source-adapter-manifest-contract.md
│   └── source-discovery-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/pipeline/
├── src/
│   ├── sources/
│   │   ├── fred_fedfunds_source.py
│   │   ├── eia_retail_fuel_prices_source.py
│   │   └── nyfed_college_labor_market_source.py
│   ├── orchestration/
│   │   ├── jobs/
│   │   │   └── source_assets/
│   │   │       └── discovery.py
│   │   ├── resources/
│   │   │   └── postgres_observation_repository.py
│   │   ├── schedules/
│   │   └── source_asset_definitions.py
│   └── contract/
├── tests/
│   ├── orchestration/
│   ├── integration/
│   ├── contract/
│   └── unit/

tools/
└── provider_bootstrap/

libs/db/
├── src/db/models/
└── alembic/versions/

apps/backend/
├── src/
│   ├── contract/query/
│   └── query/
└── tests/contract/

apps/frontend/
├── src/
│   ├── app/sources/
│   ├── components/discovery/
│   └── lib/api/
└── tests/

docs/runbooks/
.agents/skills/onboard-provider/
```

**Structure Decision**: Introduce a new top-level pipeline source package at `apps/pipeline/src/sources` and update existing discovery/bootstrap/runtime imports to treat it as the single maintained adapter surface. Preserve existing orchestration modules as consumers of discovered source specs rather than moving broader orchestration code.

## Phase 0: Research and Decisions

- Confirm the cleanest adapter relocation strategy without keeping dual active source directories.
- Confirm the source manifest contract extension for required title and description fields and how bootstrap generation should enforce them.
- Confirm the source-level persistence model so source metadata is authoritative from manifests, not reconstructed from dataset rows.
- Confirm how source list/detail identifiers should evolve so routes and APIs use stable source identity while frontend labels become human-readable.
- Confirm migration/backfill expectations for existing `source_profiles` rows and existing maintained adapters.

## Phase 1: Design and Contracts

- Define the source manifest, persisted source profile, source discovery response, and source-page view-state data model for the new metadata flow.
- Define the source adapter manifest contract for required location, required metadata fields, and validation behavior.
- Define the updated source discovery contract for stable source identifiers plus human-readable title and description in backend/frontend payloads.
- Define manual verification steps covering scaffold generation, startup discovery, migration/backfill, API payloads, and frontend rendering in the local stack.
- Update agent context after design artifacts are written.

## Phase 2: Implementation Planning

- Relocate maintained adapter modules and update pipeline discovery/registration/bootstrap tooling to scan and generate under the new source package.
- Extend `SOURCE_SPEC`/`SourceBuilderSpec` validation and bootstrap scaffolding so `title` and `description` are required and fail fast when missing.
- Add source-level persistence fields and migration/backfill behavior in `source_profiles`, then update pipeline persistence to write manifest-owned source metadata keyed by stable `source_key`.
- Update backend source query contracts and repository/service projections so source list/detail payloads expose stable identifiers, source title, and source description.
- Update frontend discovery types, source list/detail pages, and shared source presentation components to use the title as the primary label and show the description where source context is rendered.
- Refresh provider onboarding docs, local-stack guidance where needed, bootstrap examples, skill instructions, and AGENTS path/tooling references.
- Validate with focused pipeline/backend/frontend tests, clean-restart manual verification, `pre-commit run --all-files`, and mandatory monorepo-wide test and coverage gates.

## Post-Design Constitution Check

- Monorepo cohesion: PASS. The design keeps one coherent vertical slice with explicit contract changes across pipeline, DB, backend, frontend, and docs.
- Quality gate enforcement: PASS. No suppression or bypass strategy is introduced.
- Full-suite stop rule: PASS. The plan keeps `pnpm exec nx run-many -t test --all` as the mandatory stop gate.
- Coverage stop rule: PASS. The plan keeps `pnpm exec nx run-many -t coverage --all` as the mandatory coverage stop gate.
- Test and coverage discipline: PASS. The design adds coverage at every changed boundary.
- Local-first parity: PASS. The change is runnable against the existing compose stack with migration and ingest validation.
- Data integrity and reliability: PASS. Stable `source_key` identity, source-level metadata authority, and migration/backfill are explicitly designed.
- Configuration integrity: PASS. No new secrets or credential behaviors are introduced.
- Frontend UI consistency: PASS. Source title/description rendering will be implemented within existing discovery components and HeroUI/Tailwind patterns.
- Documentation fidelity: PASS. Runbooks, skills, spec artifacts, and AGENTS references are identified for update.

## Complexity Tracking

No constitution violations requiring justification.
