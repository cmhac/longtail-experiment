# Dataset Detail Chart Contract

## Scope

This contract defines the expected loaded-state, interaction, and fallback behavior for the dataset detail page trend chart.

## Route and Data Contract

- Route shape remains `/datasets/{id}`.
- The existing dataset detail payload remains the source of truth for charted observations.
- No new backend fields are required for chart rendering or range availability.

## Loaded-State Chart Contract

- A loaded dataset with observations renders a trend chart that uses the full available width of the trend section.
- The chart surface visually extends downward to align with the bottom of the adjacent metadata column in the detail-page analysis layout.
- The chart renders without an enclosing border around the plotting area.
- The chart does not render the previous observation-count footnote beneath the plot.
- The chart line renders without visible point dots in the default state.
- X-axis labels are presented with clearer separation than the prior chart behavior.

## Range Control Contract

- All-history is the default selected range whenever observations exist.
- Visible range controls are ordered from longest to shortest, left to right.
- The available range set may include all-history, 5-year, 1-year, 6-month, and 1-month options.
- The 5-year option appears only when the dataset history meaningfully supports it.
- Any unsupported range is hidden rather than shown in a disabled or inactive state.
- If no preset ranges beyond all-history are meaningfully supported, the time-filter control group is hidden entirely.
- Every visible time-filter button presents a pointer cursor for pointer-device users.

## Interaction Contract

- Selecting a visible range updates the chart to the corresponding filtered historical view.
- Every visible range must produce a meaningful chart state distinct from broader visible ranges or all-history.
- The selected range must always be one of the currently visible range options.

## Fallback Contract

- If there are no observations, the chart area shows explicit no-data messaging.
- No-data chart states do not render dead-end time-filter controls.
- Existing detail-page generic error and not-found behaviors remain unchanged.

## Responsive Contract

- Desktop and mobile layouts preserve chart readability, visible control usability, and section alignment intent.
- Chart controls and axis labels do not clip or overlap in supported viewport ranges.
