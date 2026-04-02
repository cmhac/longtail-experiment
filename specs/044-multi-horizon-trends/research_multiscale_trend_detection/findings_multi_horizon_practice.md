# Findings: Multi-Horizon Practice in Finance/Economics

## Scope

How practitioners operationalize short/intermediate/long trend systems and reconcile conflicting signals.

## Key Findings

- Multi-horizon analysis is typically hierarchical, not flat. Teams treat horizons as different decision layers (context vs timing).
- Common operational pattern: long horizon sets directional bias, medium horizon sets positioning, short horizon sets entry/exit timing.
- Conflict handling is explicit in mature systems (for example: reduced position size when horizons conflict; abstain in high-conflict zones).
- Systems that require cross-horizon confirmation usually reduce whipsaw risk at the cost of slower reaction.

## What This Means For Your Concern

- Your concern is conceptually correct: trend periods are horizon-dependent.
- Asking one detector to produce one "canonical" segmentation for all user intents often produces broad or unstable spans.
- A practical alternative is to provide separate trend layers (for example short/medium/long) and make conflict explicit rather than forcing one answer.

## Operational Patterns To Borrow

- Define horizon taxonomy up front (for example weeks, months, years).
- Define deterministic conflict policy:
  - align -> full confidence
  - mixed -> reduced confidence/size
  - contradictory -> neutral or no-trade/no-strong-label state
- Keep each horizon independently testable and backtestable.
- Track horizon-level quality metrics separately (precision/recall/stability/latency).

## Risks and Caveats

- More horizons increase product complexity and user confusion unless UI explicitly communicates hierarchy.
- Overfitting risk increases if each horizon has many tunables.
- Governance is required to avoid silent drift of horizon-specific behavior.

## Sources

- Market trend framing (multi-timescale language): https://en.wikipedia.org/wiki/Market_trend
- Time-series methods and decomposition context: https://en.wikipedia.org/wiki/Time_series
- Practical channel/trend context (illustrative practitioner framing): https://www.investopedia.com/
- Technical analysis critique and limitations context (for caution): https://en.wikipedia.org/wiki/Technical_analysis
