#!/usr/bin/env bash
set -euo pipefail

start=$(date +%s)
pnpm nx affected -t lint --files=apps/pipeline/src/__init__.py
end=$(date +%s)
elapsed=$((end - start))
if [[ "$elapsed" -gt 180 ]]; then
  echo "Affected lint took ${elapsed}s, exceeding 180s target" >&2
  exit 1
fi
echo "Affected lint completed in ${elapsed}s"
