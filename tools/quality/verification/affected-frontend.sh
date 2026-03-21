#!/usr/bin/env bash
set -euo pipefail

pnpm nx affected -t lint --files=apps/frontend/src/main.ts
pnpm nx affected -t test --files=apps/frontend/tests/smoke.test.ts
pnpm nx affected -t test --files=apps/pipeline/tests/test_smoke.py
