# Contract: Pipeline to Backend Baseline Handoff

## Purpose

Define baseline upstream/downstream boundaries where pipeline feeds backend and backend
serves frontend, without implementing production data logic.

## Boundary Roles

- Pipeline role: upstream placeholder producer.
- Backend role: downstream placeholder consumer and frontend-serving boundary.
- Frontend role: backend consumer only; no direct pipeline coupling.

## Baseline Interface Expectations

- Pipeline MUST expose a placeholder-ready integration boundary for backend consumption.
- Backend MUST remain the only serving interface to frontend in this baseline phase.
- Any future handoff payload/schema details MUST be versioned and documented before
  implementation.
- Baseline placeholder connectivity uses service-level health and startup verification,
  not production payload exchange.

## Verification Contract

- Local stack verification MUST confirm all three services are healthy.
- Workspace smoke tests MUST verify pipeline project registration and command discoverability.
- Contract documentation updates are mandatory when handoff assumptions change.

## Non-Goals

- Defining production payload schema fields in this phase.
- Implementing real extraction/transformation/load workflows.
- Implementing backend business processing of pipeline outputs.
