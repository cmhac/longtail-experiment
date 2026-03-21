#!/usr/bin/env bash
set -euo pipefail

pnpm nx affected -t lint --files=nx.json
pnpm nx affected -t duplication --files=nx.json
pnpm nx affected -t lint --files=apps/pipeline/project.json
