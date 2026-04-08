# Chosen Tools

- `scipy.stats.theilslopes`: Primary robust slope estimation for per-lookback trend scoring.
- `scipy.stats.kendalltau`: Monotonic trend evidence input used to modify confidence.
- `pandas.Series.ewm`: Default EWMA preprocessing/smoothing.
- `statsmodels.tsa.seasonal.STL`: Seasonal adjustment for monthly/weekly single-season cadence cases.
- `statsmodels.tsa.seasonal.MSTL`: Seasonal adjustment for regular sub-daily multi-season cadence cases.
- `ruptures`: Change-point detection metadata for tie-break/context signals.
- `statsmodels` OLS: Supplementary OLS diagnostic field computation for detail/as-of trend payloads.
