# Research: Provider Adapter Bootstrap Standard

## Decision 1: Scaffold generation mechanism

- Decision: Implement bootstrap generation using a repository-owned template and Python standard-library rendering/placeholder substitution.
- Rationale: Keeps generation deterministic, avoids adding a new external dependency for a simple scaffold, and aligns with existing Python tooling in the pipeline workspace.
- Alternatives considered:
  - Jinja2 dependency: flexible, but unnecessary for first implementation and adds dependency management overhead.
  - Shell heredoc-only generation: fast to write but harder to maintain, test, and evolve for multi-series scaffolds.

## Decision 2: Bootstrap interface shape

- Decision: Define a single root-level command with required provider/source inputs and optional multi-series fields; enforce validation before writing files.
- Rationale: One discoverable command reduces onboarding drift and supports both humans and coding agents consistently.
- Alternatives considered:
  - Interactive prompt mode only: less CI/automation-friendly.
  - Multiple specialized commands: increases cognitive overhead and documentation surface.

## Decision 3: Collision protection

- Decision: Fail hard when target file already exists or when requested source identity conflicts with existing adapter identities.
- Rationale: Prevents accidental overwrite and preserves source-key uniqueness expectations in dynamic discovery.
- Alternatives considered:
  - Auto-overwrite with flag defaults: too risky for onboarding artifacts.
  - Auto-rename on conflict: creates hidden divergence from requested provider identity.

## Decision 4: Scaffold baseline content

- Decision: Generated module includes required onboarding structure: source key constant, workflow builder shell, source spec skeleton, placeholder metadata fields, and comments guiding completion.
- Rationale: Matches existing adapter contract and gives both developers and agents a clean, reviewable starting point.
- Alternatives considered:
  - Minimal empty file plus TODO links: insufficient guardrails and likely to reintroduce onboarding inconsistency.
  - Full provider implementation generation: unrealistic without provider-specific API/domain details.

## Decision 5: Documentation and agent-standard enforcement

- Decision: Update provider onboarding runbook and onboarding skill so bootstrap usage is the standard first step, and require runbook consultation in agent workflows.
- Rationale: Tooling alone does not enforce behavior; guidance and agent constraints must align to create a true standard path.
- Alternatives considered:
  - Documentation-only update: leaves agent behavior unconstrained.
  - Skill-only update: leaves human contributor onboarding inconsistent.

## Decision 6: Test strategy for this feature

- Decision: Add generator behavior tests (valid creation, invalid input, collision handling, scaffold structure assertions) and keep existing orchestration/discovery tests as regression safety net.
- Rationale: Directly validates feature requirements while preserving confidence that generated files conform to runtime expectations.
- Alternatives considered:
  - Manual-only verification: insufficient for a standard onboarding mechanism.
  - Full end-to-end compose-only validation: useful but slower and less precise than unit-level generator tests.
