# Research: Frontend Page Furniture Baseline

## Decision 1: Use Next.js App Router as the baseline shell runtime

- Decision: Adopt a minimal App Router structure for the root route and shell composition.
- Rationale: App Router provides stable layout composition primitives and aligns with issue guidance for SSR-ready baseline behavior.
- Alternatives considered:
  - Keep current non-Next placeholder entrypoint.
    - Rejected because it does not provide framework-managed routing/runtime boundaries.
  - Use legacy Pages Router.
    - Rejected because there is no identified compatibility blocker that requires it for this scaffold.

## Decision 2: Implement furniture through local typed adapter contracts

- Decision: Define local furniture slot contracts and wire placeholder adapters for top nav, secondary nav, footer, scripts/analytics, and ads/subscription slots.
- Rationale: Adapter boundaries allow provider swaps later without refactoring the root page or shell composition.
- Alternatives considered:
  - Render all placeholder markup directly inside the root page.
    - Rejected because it couples page structure to implementation details and weakens extension boundaries.
  - Depend on provider-specific packages immediately.
    - Rejected because issue scope requires a no-private-dependency baseline.

## Decision 3: Add process-hook stubs as explicit lifecycle contracts

- Decision: Create contract-first server hook stubs for environment bootstrap, data bootstrap extension, and publish extension.
- Rationale: Early lifecycle boundaries reduce future integration churn and make ownership explicit for upcoming workflow integrations.
- Alternatives considered:
  - Delay hook contracts until feature integrations begin.
    - Rejected because later insertion would require broad shell/server rewiring.
  - Add fully implemented business logic now.
    - Rejected because current scope is scaffold only.

## Decision 4: Verify readiness with both visual shell checks and quality gates

- Decision: Require local startup verification of shell/furniture placeholders plus lint/format/typecheck/test/coverage checks for affected frontend scope.
- Rationale: This ensures both runtime validity and repository policy compliance before follow-on feature development.
- Alternatives considered:
  - Run only automated tests without visual verification.
    - Rejected because issue acceptance criteria include confirming the page looks structurally correct.
  - Perform only manual browser checks.
    - Rejected because this does not guarantee enforceable regression protection.

## Decision 5: Preserve empty main content region as a non-negotiable scope guardrail

- Decision: Root route keeps main content intentionally blank while furniture placeholders remain visible.
- Rationale: The objective is environment and shell validation, not product feature delivery.
- Alternatives considered:
  - Add sample editorial or product content.
    - Rejected because it violates issue scope and can hide shell-only regressions.
