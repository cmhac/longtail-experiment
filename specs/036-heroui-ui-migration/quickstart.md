# Quickstart: Frontend UI Standardization Migration

## Goal

Validate the HeroUI/Tailwind standardization work across the existing frontend without changing discovery behavior or losing Longtail’s established visual identity.

## Prerequisites

- Dependencies installed from the repo root:
  - `pnpm install`
- Frontend dependencies synchronized if needed:
  - `pnpm --dir apps/frontend install`
- Backend/discovery API available through the normal local environment if doing end-to-end route checks

## Recommended Workflow

### 1. Confirm clean frontend bootstrap

Run:

```bash
pnpm --dir apps/frontend typecheck
pnpm --dir apps/frontend exec biome check .
```

Expected result:

- TypeScript passes
- Biome passes
- no invalid HeroUI bootstrap or styling-import regressions

### 2. Run focused frontend regression tests during development

Run targeted tests for changed areas, for example:

```bash
pnpm --dir apps/frontend test -- DatasetListControls.test.tsx
pnpm --dir apps/frontend test -- search-page.test.tsx
pnpm --dir apps/frontend test -- home-page.test.tsx
pnpm --dir apps/frontend test -- UnifiedDatasetRow.test.tsx
```

Expected result:

- changed shell/discovery surfaces preserve behavior while DOM/style structure evolves

### 3. Start the frontend for manual UI review

Run:

```bash
pnpm --dir apps/frontend dev
```

Review these routes:

- `/`
- `/search?q=rate`
- `/datasets`
- `/datasets/[known-id]`
- `/sources`
- `/sources/[known-source]`
- `/topics/[known-topic]`
- `/geographies/[known-geography]`

Manual checks:

- shell/header/footer look standardized but still recognizably Longtail
- typography remains correct
- color intent remains correct in light and dark contexts
- search hero and navbar search both work
- filter/sort controls remain usable
- list rows/cards/headers share a consistent surface language
- empty/error states remain explicit
- route navigation still works normally

### 4. Validate responsive behavior

Check at least:

- desktop width
- tablet width
- narrow mobile width

Expected result:

- controls remain readable and operable
- no broken wrapping or clipped content
- page structure remains understandable

### 5. Run project stop gates before handoff or commit

Required commands:

```bash
pnpm exec nx run-many -t test --all
pnpm exec nx run-many -t coverage --all
pre-commit run --all-files
```

Expected result:

- full monorepo tests pass
- full monorepo coverage passes at configured thresholds
- all-files quality gate passes

## Suggested Manual Audit Checklist

- Header navigation uses standardized controls and spacing.
- Footer uses the same surface language as the rest of the shell.
- Search surfaces feel like one system across homepage and navbar.
- Dataset list controls, rows, and cards no longer rely on obviously bespoke one-off presentation.
- Dataset detail and metadata pages match the same container language as list pages.
- Any intentionally custom data-dense surface is visibly deliberate and documented as an exception.
