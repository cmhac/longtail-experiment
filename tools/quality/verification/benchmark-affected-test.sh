#!/usr/bin/env bash
set -euo pipefail

start=$(date +%s)
pnpm nx affected -t test --files=apps/frontend/tests/smoke.test.ts
end=$(date +%s)
elapsed=$((end - start))
if [[ "$elapsed" -gt 180 ]]; then
  echo "Affected test took ${elapsed}s, exceeding 180s target" >&2
  exit 1
fi
echo "Affected test completed in ${elapsed}s"
