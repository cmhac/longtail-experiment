# Monorepo Boundaries

## Purpose

Define ownership and separation boundaries for baseline monorepo projects.

## Project Boundaries

- apps/pipeline: Python Dagster-oriented pipeline placeholder and pipeline quality targets.
- apps/backend: Python backend placeholder and backend quality targets.
- apps/frontend: TypeScript frontend placeholder and frontend quality targets.
- tools/quality: Shared duplication and verification tooling.
- docker-compose.yml: Local stack orchestration for pipeline, backend, and frontend placeholders only.

## Rules

- No product business logic is allowed in baseline placeholders.
- Pipeline is upstream of backend placeholders, and frontend only consumes backend boundaries.
- Cross-project dependencies must be explicit and minimal.
- Quality targets must remain project-scoped and affected-aware.
