# Local Stack Baseline Runbook

## Start

1. Run docker compose up -d
2. Run docker compose ps

## Healthy State

- backend service is listed and healthy.
- frontend service is listed and healthy.

## Troubleshooting

- If backend is unhealthy, inspect: docker compose logs backend
- If frontend is unhealthy, inspect: docker compose logs frontend
- If either service fails health checks, stop stack with docker compose down and fix configuration before retry.
