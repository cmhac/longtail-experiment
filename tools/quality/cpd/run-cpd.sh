#!/usr/bin/env bash
set -euo pipefail

if command -v pmd >/dev/null 2>&1; then
  PMD_CMD="pmd"
elif [[ -x "$HOME/pmd-bin-7.22.0/bin/pmd" ]]; then
  PMD_CMD="$HOME/pmd-bin-7.22.0/bin/pmd"
else
  echo "PMD not found. Run tools/quality/pmd/install-pmd.sh first." >&2
  exit 1
fi

"$PMD_CMD" cpd --minimum-tokens 50 --dir apps/backend/src --dir apps/frontend/src --dir apps/pipeline/src
