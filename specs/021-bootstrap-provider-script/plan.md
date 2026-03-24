# Implementation Plan: Provider Adapter Bootstrap Standard

**Branch**: `021-bootstrap-provider-script` | **Date**: 2026-03-24 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/spec.md)
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/spec.md`

## Summary

Deliver a standard monorepo bootstrap command that generates a provider adapter scaffold as the canonical starting point for onboarding, then align both human and agent onboarding guidance to require this script-first path.

The implementation will add a deterministic scaffold generator under repository tooling, expose it via root package scripts, enforce collision and input validation behavior, and update the onboarding runbook and onboarding skill to make script usage mandatory for new adapters.

## Technical Context

**Language/Version**: Python 3.12 for pipeline tooling and TypeScript/Node.js 22 for root script wiring  
**Primary Dependencies**: Existing repository toolchain (pnpm workspace, Nx, Python stdlib templating); no mandatory new runtime dependency  
**Storage**: File generation in workspace tree (adapter module path under pipeline sources); no new persistent datastore  
**Testing**: pytest (pipeline/tooling tests), existing orchestration contract tests, optional script invocation smoke tests via Nx/pnpm  
**Target Platform**: Local developer environments and CI on macOS/Linux shells using repository scripts  
**Project Type**: Monorepo tooling enhancement plus documentation and agent-guidance update  
**Performance Goals**: Scaffold generation completes in under 2 seconds for normal invocations  
**Constraints**: Must preserve dynamic source discovery contract, must not overwrite existing adapters, must keep quality gates and full-suite/coverage stop rules intact  
**Scale/Scope**: One new bootstrap workflow, one generated adapter module at a time, documentation and skill updates across onboarding surfaces

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS - changes remain within existing monorepo boundaries (`apps/pipeline`, root scripts, docs, agent skill) with no new project boundary violations.
- Quality gate enforcement: PASS - plan includes lint, format, typecheck, test, and coverage validation without suppression strategy.
- Full-suite stop rule: PASS - implementation completion criteria include `pnpm exec nx run-many -t test --all` before commit/handoff.
- Coverage stop rule: PASS - implementation completion criteria include `pnpm exec nx run-many -t coverage --all` with per-project minimums.
- Test and coverage discipline: PASS - adds/updates tests for generator behavior (valid input, invalid input, collision detection, scaffold shape).
- Local-first parity: PASS - no new services; output is source files consumed by existing local compose stack and runtime.
- Data integrity and reliability: PASS - no schema or provenance contract changes; generated scaffold follows existing canonical adapter shape.
- Configuration integrity: PASS - feature introduces no new credential-bearing service and does not relax fail-hard credential rules.
- Documentation fidelity: PASS - explicitly updates `docs/runbooks/provider-onboarding.md`, `.agents/skills/onboard-provider/SKILL.md`, and command discoverability in root package scripts/docs.

Post-design re-check: PASS on all gates. No constitution violations identified.

## Phase 0 Research Outcomes

See `/Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/research.md`.

- Resolved generator approach: use repository-owned template file plus Python standard-library templating and argument validation.
- Resolved interface contract: explicit CLI command contract documented under `contracts/`.
- Resolved integration pattern: keep generated module aligned with dynamic discovery rules (`*_source.py` filename, `SOURCE_SPEC` contract fields, builder function shell).

## Phase 1 Design Artifacts

- Data model: `/Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/data-model.md`
- Interface contract: `/Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/contracts/provider-bootstrap-cli.md`
- Quickstart: `/Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/quickstart.md`
- Agent context update executed via `.specify/scripts/bash/update-agent-context.sh codex`

## Project Structure

### Documentation (this feature)

```text
specs/021-bootstrap-provider-script/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── provider-bootstrap-cli.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── pipeline/
    ├── src/orchestration/jobs/sources/
    │   └── <generated_provider>_source.py
    └── tests/
        └── ... (generator/scaffold validation tests)

.agents/
└── skills/
    └── onboard-provider/
        └── SKILL.md

docs/
└── runbooks/
    └── provider-onboarding.md

tools/
└── ... (bootstrap script/template location selected during implementation)

package.json
```

**Structure Decision**: Keep implementation inside existing monorepo surfaces (pipeline tooling plus docs/skill updates) and avoid introducing new apps/libs. Root `package.json` exposes the bootstrap command for consistent invocation.

## Implementation Phases

### Phase 2 Delivery Plan

1. Add bootstrap script and template asset for adapter scaffold generation.
2. Add input normalization and validation (provider/source keys, series mapping, file suffix requirements).
3. Add collision checks for filesystem target and existing source identity references.
4. Wire command into root `package.json` scripts and document invocation.
5. Add/adjust tests for success path and failure paths.
6. Update provider onboarding runbook to require script-first onboarding.
7. Update onboarding agent skill to require runbook review and script usage.
8. Run required quality and stop-gate commands.

### Verification Plan

- Focused tests while developing:
  - generator unit tests
  - scaffold-shape assertions
  - collision/error-path tests
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.
