# Contract: Local Stack Three-App Baseline

## Purpose

Define the local Docker Compose baseline contract after adding the pipeline app.

## Compose Contract

- A single root `docker-compose.yml` MUST orchestrate pipeline, backend, and frontend
  placeholder services.
- Each service MUST include health check criteria.
- Startup and shutdown commands MUST remain single-flow developer operations.

## Service Contract

- Pipeline placeholder service MUST start with baseline environment profile.
- Backend placeholder service MUST start and remain the frontend-serving boundary.
- Frontend placeholder service MUST start and rely on backend boundary only.
- Baseline service ports are 8090 (pipeline), 8080 (backend), and 3000 (frontend).

## Verification Contract

- `docker compose up -d` MUST start all three services.
- Health verification MUST complete within 5 minutes on a standard developer machine.
- `docker compose down` MUST stop and clean up services deterministically.

## Failure Behavior Contract

- If any service is unhealthy, stack verification MUST fail overall.
- Failure output MUST include actionable diagnostics for the failing service.
