# Monotonic Evidence Tooling (Kendall tau / Mann-Kendall) in Python

## Scope
- Focused on Python tooling and practical interpretation for monotonic trend evidence in time series.
- Sources limited to 5 web lookups.

## Candidate Libraries and What They Provide

### 1) SciPy (`scipy.stats.kendalltau`)
- Computes Kendall rank correlation (tau-b default, tau-c optional) and p-value for null `tau = 0`.
- Supports `alternative` (`two-sided`, `less`, `greater`) and p-value `method` (`auto`, `asymptotic`, `exact`).
- Important constraint: `method='exact'` is only valid when there are no ties.
- Output semantics are clean for weighting systems: `SignificanceResult(statistic=<tau>, pvalue=<p>)`.
- Also exposes related robust trend tools via `scipy.stats.theilslopes` and `scipy.stats.weightedtau` in the same ecosystem.

Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html

## Caveats: Serial Correlation and Seasonality

### Serial correlation caveat
- MK-style tests assume independence over time under the null; autocorrelation can inflate apparent significance.
- If autocorrelation is present, prefer corrected MK variants (variance correction or pre-whitening), and treat uncorrected test evidence as down-weighted.

Primary sources:
- https://vsp.pnnl.gov/help/vsample/design_trend_mann_kendall.htm

### Seasonality caveat
- Standard MK can mislead for strongly seasonal series; use seasonal MK variants that aggregate within-season evidence.
- If seasonality is unresolved, reduce confidence contribution from monotonic evidence instead of forcing binary reject/accept behavior.

Primary sources:
- https://vsp.pnnl.gov/help/vsample/design_trend_mann_kendall.htm

## Output Semantics to Preserve in Downstream Trend Systems

- **Directionality**: sign of `tau`, sign of Sen slope, and in MK packages trend labels (`increasing` / `decreasing` / `no trend`).
- **Strength of evidence**: p-value (`p`/`pvalue`) and standardized statistic (`z`) where provided.
- **Magnitude**: Sen slope (`slope`) and confidence interval bounds (`lcl`, `ucl`) where available.
- **Method metadata**: which correction was used (original, pre-whitened, seasonal, variance-corrected).

Practical recommendation: store these as separate fields and avoid collapsing to one Boolean early.

## Patterns for Weighted Confidence Modifiers (Not Hard Gates)

Use MK/Kendall outputs as continuous evidence modifiers in your trend scoring model:

1. Build a signed evidence term from direction and effect size, e.g. `sign(slope) * f(|tau|, |slope|)`.
2. Convert statistical support to a soft weight, e.g. `w_p = 1 - min(1, p / p_cap)` or a smooth transform of `-log10(p)`.
3. Apply quality penalties multiplicatively for caveats:
   - autocorrelation unresolved: multiply by `penalty_ac < 1`
   - seasonality unresolved: multiply by `penalty_season < 1`
   - small n / many ties: multiply by `penalty_sample < 1`
4. Aggregate multiple monotonic diagnostics as an ensemble (e.g., Kendall tau + corrected MK + seasonal MK), then average/stack weights.
5. Keep a floor and ceiling (e.g. `[0.05, 0.95]`) to prevent any single test from becoming a hard gate.

Why this pattern is source-aligned:
- MK is often framed as exploratory, and assumptions violations can bias significance; weighting preserves signal without brittle pass/fail behavior.

Source anchor for exploratory framing: https://vsp.pnnl.gov/help/vsample/design_trend_mann_kendall.htm

## Relevant Quotes

> "Kendall’s tau is a measure of the correspondence between two rankings. Values close to 1 indicate strong agreement, and values close to -1 indicate strong disagreement."  
Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html

> "The p-value for a hypothesis test whose null hypothesis is an absence of association, tau = 0."  
Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html

> "Hirsch, Slack and Smith (1982, page 107) indicate that the MK test is best viewed as an exploratory analysis..."  
Source: https://vsp.pnnl.gov/help/vsample/design_trend_mann_kendall.htm

## Source URLs (All consulted)
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html
- https://vsp.pnnl.gov/help/vsample/design_trend_mann_kendall.htm
