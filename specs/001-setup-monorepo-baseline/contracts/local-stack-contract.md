# Contract: Local Stack Baseline

## Purpose

Define the baseline local full-stack interface that must be runnable before any product logic exists.

## Compose Contract

- A single root-level `docker-compose.yml` MUST orchestrate the local baseline stack.
- The stack MUST include placeholder backend and frontend services.
- Each service MUST expose a health check with clear healthy/unhealthy criteria.
- Startup and shutdown commands MUST be documented in quickstart.

## Service Contract

- Backend placeholder service:
  - MUST start successfully with baseline environment profile.
  - MUST provide a health endpoint or equivalent readiness signal.
- Frontend placeholder service:
  - MUST start successfully with baseline environment profile.
  - MUST provide a health endpoint or equivalent readiness signal.

## Verification Contract

- Developers MUST be able to run a single startup command for the stack.
- Stack health verification MUST complete within 5 minutes on a standard machine.
- Developers MUST be able to run a single shutdown command.

## Failure Behavior Contract

- If any service fails to become healthy, the workflow MUST produce actionable logs.
- Failure in one service MUST fail the overall baseline verification.

## Scope Boundaries

- The local stack in this feature is scaffolding only and MUST NOT include business feature endpoints or domain workflows.
- Product data ingest, trend analysis, and alerting implementations are explicitly out of scope.
