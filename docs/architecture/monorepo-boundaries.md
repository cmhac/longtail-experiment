# Monorepo Boundaries

## Purpose

Define ownership and separation boundaries for baseline monorepo projects.

## Project Boundaries

- apps/backend: Python backend placeholder and backend quality targets.
- apps/frontend: TypeScript frontend placeholder and frontend quality targets.
- tools/quality: Shared duplication and verification tooling.
- docker-compose.yml: Local stack orchestration for placeholder services only.

## Rules

- No product business logic is allowed in baseline placeholders.
- Cross-project dependencies must be explicit and minimal.
- Quality targets must remain project-scoped and affected-aware.
