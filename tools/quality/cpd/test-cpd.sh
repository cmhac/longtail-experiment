#!/usr/bin/env bash
set -euo pipefail

grep -q "apps/pipeline/src" tools/quality/cpd/run-cpd.sh
bash tools/quality/cpd/run-cpd.sh
