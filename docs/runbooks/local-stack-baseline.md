# Local Stack Baseline Runbook

## Start

1. Run docker compose up -d
2. Run docker compose ps

## Healthy State

- pipeline service is listed and healthy.
- backend service is listed and healthy.
- frontend service is listed and healthy.

## Troubleshooting

- If backend is unhealthy, inspect: docker compose logs backend
- If frontend is unhealthy, inspect: docker compose logs frontend
- If pipeline is unhealthy, inspect: docker compose logs pipeline
- If any service fails health checks, stop stack with docker compose down and fix configuration before retry.
