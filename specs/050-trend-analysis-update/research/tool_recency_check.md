# Tool Recency Verification (Spec 050 Research)

Date checked: 2026-04-07 (UTC)
Policy applied: exclude tools with latest release older than 1 year.

## Included (recent enough)

- `scipy` — latest release `1.17.1`, uploaded `2026-02-23T00:26:24Z`
- `scikit-learn` — latest release `1.8.0`, uploaded `2025-12-10T07:08:53Z`
- `pandas` — latest release `3.0.2`, uploaded `2026-03-31T06:48:30Z`
- `statsmodels` — latest release `0.14.6`, uploaded `2025-12-05T23:15:24Z`
- `ruptures` — latest release `1.1.10`, uploaded `2025-09-10T09:48:02Z`
- `river` — latest release `0.23.0`, uploaded `2025-11-13T19:25:11Z`
- `hmmlearn` — latest release `0.3.3`, uploaded `2024-10-31T09:04:20Z`

## Excluded (outdated by policy)

- `pymannkendall` — latest release `1.4.3`, uploaded `2023-01-14T08:40:24Z`
- `mannkendall` — latest release `1.1.1`, uploaded `2022-07-08T06:33:06Z`
- `kats` — latest release `0.2.0`, uploaded `2022-03-15T16:02:45Z`

## Research file updates performed

- Removed all mentions of outdated tools from:
  - `specs/050-trend-analysis-update/research/findings_theil_sen.md`
  - `specs/050-trend-analysis-update/research/findings_monotonic_evidence.md`
  - `specs/050-trend-analysis-update/research/findings_change_point.md`

Data source for release timestamps: PyPI JSON API (`https://pypi.org/pypi/<package>/json`).
