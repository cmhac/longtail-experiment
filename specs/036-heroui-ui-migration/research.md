# Research: Frontend UI Standardization Migration

## Decision 1: Use canonical HeroUI v3 + Tailwind CSS v4 bootstrap in the frontend

- Decision: Standardize `apps/frontend` on the documented HeroUI v3 bootstrap pattern: Tailwind CSS v4 first, `@heroui/styles` second, with no HeroUI provider.
- Rationale: HeroUI v3 documentation defines Tailwind CSS v4 plus `@heroui/styles` as the canonical styling path. The current frontend already has PostCSS configured for Tailwind v4, but `globals.css` imports `@heroui/react/styles` directly and the app still relies on a large custom CSS shell. Moving to the canonical bootstrap gives the migration a stable foundation and aligns future work with the library’s intended patterns.
- Alternatives considered:
  - Keep the current `@heroui/react/styles` import and only refactor components. Rejected because it leaves the migration without the library’s documented baseline and keeps the style stack ambiguous.
  - Introduce a provider-based wrapper. Rejected because HeroUI v3 explicitly does not require a provider for basic usage.

## Decision 2: Preserve current typography and color identity through theme variables, not bespoke per-component CSS

- Decision: Keep Longtail’s existing typography families and color intent by mapping them into the app’s theme variables and minimal global theme CSS rather than re-implementing them on each component.
- Rationale: The feature spec explicitly protects typography and color identity. HeroUI v3 theming is CSS-variable based, which fits the current frontend’s `globals.css` variable strategy and allows preserving the recognizable brand surface while still using HeroUI and Tailwind defaults for structure, spacing, and component behavior.
- Alternatives considered:
  - Replace all existing visual tokens with HeroUI defaults. Rejected because it would violate the preserved-identity requirement in the feature spec.
  - Keep the current shell CSS untouched and only swap components. Rejected because it would preserve too many bespoke layout and surface rules, undermining the standardization goal.

## Decision 3: Prefer HeroUI components, Tailwind utilities, and HeroUI variant functions over bespoke wrapper markup

- Decision: For in-scope shared UI surfaces, use HeroUI primitives and Tailwind utilities first; use HeroUI variant functions or BEM classes for framework-specific roots such as `next/link`; keep custom wrappers only where they preserve necessary behavior or brand identity.
- Rationale: Current discovery components mix HeroUI primitives with raw HTML and large custom class systems. HeroUI v3 documentation emphasizes composition, semantic variants, Tailwind-friendly styling, and framework-agnostic variant functions. That model fits the current Next.js app and reduces the amount of custom CSS and duplicated surface logic.
- Alternatives considered:
  - Rebuild a custom in-house component layer on top of HeroUI. Rejected because it would add indirection and duplicate what HeroUI already provides.
  - Apply direct Tailwind classes to all HTML elements without using HeroUI primitives. Rejected because the feature specifically aims for near-complete HeroUI usage and wants to replace non-HeroUI components where practical.

## Decision 4: Migrate the frontend in dependency order: foundation, shell, controls, shared surfaces, pages

- Decision: Sequence the work as foundation/theme bootstrap first, then shell, then shared controls, then repeated content surfaces, then route integration.
- Rationale: The current frontend architecture is route pages composed from shared discovery and shell components. Standardizing shared layers first minimizes churn in page files and reduces the risk of multiple local restylings of the same pattern.
- Alternatives considered:
  - Refactor route pages one by one from the outside in. Rejected because it would duplicate work across pages and allow inconsistent local patterns to persist longer.
  - Start with detail pages or charts first. Rejected because those areas depend on the broader shell/surface language and are more effective once shared patterns are already defined.

## Decision 5: Treat charts and dense tables as controlled exceptions for internal markup, but standardize their surrounding surfaces

- Decision: Preserve Recharts and existing data-table functionality, standardize the surrounding cards/headers/labels/actions first, and only replace internal markup where a HeroUI pattern improves clarity without reducing density.
- Rationale: The spec allows exceptions when necessary for product clarity. Data-dense analytical views are the most likely place where strict component replacement can harm readability. Standardizing their containers and supporting chrome still delivers consistency while avoiding unnecessary regression risk.
- Alternatives considered:
  - Force complete internal replacement of chart/table-adjacent structures. Rejected because it introduces high layout and readability risk without guaranteed user value.
  - Exclude detail analysis surfaces from the migration. Rejected because the feature scope covers primary routes and shared surfaces across the frontend.

## Decision 6: Keep existing Next.js App Router data flow and discovery client boundaries unchanged

- Decision: Limit this feature to UI-system migration and avoid backend/discovery contract changes unless a UI refactor exposes a genuine gap.
- Rationale: Existing pages already fetch through `apps/frontend/src/lib/api/discovery-client.ts` and compose server components plus client widgets cleanly. The spec focuses on refactoring and cleanup of UI, not changing product behavior or backend interfaces. Preserving those boundaries keeps risk and scope controlled.
- Alternatives considered:
  - Fold API and data contract cleanup into this feature. Rejected because it broadens the feature beyond the current user need and increases cross-layer regression risk.

## Decision 7: Use the current frontend test suite as the migration safety net and expand it where DOM semantics change

- Decision: Keep existing page/component tests as the core regression net and update them where HeroUI-driven markup or accessibility semantics change. Add targeted new tests for any newly standardized shared surface where prior coverage is weak.
- Rationale: The frontend already has broad Vitest coverage across shell, pages, controls, discovery client behavior, and state components. A UI migration changes DOM structure and interaction semantics, so tests need to track those changes instead of being bypassed or rewritten wholesale.
- Alternatives considered:
  - Rely primarily on manual visual checks. Rejected because repository policy requires automated coverage discipline and full-suite stop gates.
  - Freeze tests and preserve old markup signatures exactly. Rejected because standardization work will legitimately change markup and accessibility semantics.

## Decision 8: Document retained exceptions explicitly in a UI standardization contract

- Decision: Create a feature-local UI contract that defines migrated surfaces, allowed standardized patterns, protected identity guardrails, and the rule for documenting retained exceptions.
- Rationale: The feature spec requires bounded completion and documented exceptions. A written contract prevents the migration from becoming an open-ended cleanup effort and gives later task breakdowns a stable acceptance baseline.
- Alternatives considered:
  - Track exceptions informally in code review only. Rejected because it weakens traceability and makes feature completion subjective.
