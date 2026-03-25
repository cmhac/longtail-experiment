# Contract: Global Footer Shell Presentation

## Interface Summary

- Interface type: UI shell contract
- Consumer: All shell-rendered frontend pages
- Provider: Shared footer shell component

## Contract Elements

### Footer Container

- Must render in the shell footer region.
- Must span full page width.
- Must preserve shell layout ordering: header -> main -> footer.
- Must render as a semantic `<footer>` landmark and expose `data-testid="shell-footer"`.
- Must include a content wrapper with `data-testid="footer-content-container"`.

### Footer Content

- Required brand text: Longtail
- Required mission statement: "An editorial archive of time series data across sources, topics, and geographies."
- Content hierarchy: brand text has higher visual emphasis than mission text
- Required content test IDs: `footer-brand` and `footer-mission`
- Must not introduce utility-link clusters in the footer body

### Visual and Layout Guarantees

1. Content remains left-aligned in a padded readable area.
2. Footer remains readable in light and dark modes.
3. Footer text wraps cleanly on mobile viewports.
4. Footer content appears consistently across all shell pages.
5. Footer styling uses shell monochrome/readable token classes.

## Failure/Degradation Expectations

- If footer content cannot load, page remains functional and no blocking error state is introduced.
- Missing optional decorative styling must not remove required footer text content.

## Versioning

- Contract version: 1.0
- Breaking visual/content contract changes require updates to shell structure tests and homepage/page-level integration tests.
