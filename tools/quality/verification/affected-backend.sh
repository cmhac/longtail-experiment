#!/usr/bin/env bash
set -euo pipefail

pnpm nx affected -t lint --files=apps/backend/src/__init__.py
pnpm nx affected -t test --files=apps/backend/tests/test_smoke.py
pnpm nx affected -t lint --files=apps/pipeline/src/__init__.py
