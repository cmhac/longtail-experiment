"use client";

import React from "react";
import type { JSX } from "react";
import { Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import type { ObservationPoint } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";
import {
  DEFAULT_RELATIVE_CHANGE_SETTINGS,
  type RelativeChangeSettings,
  type TrendRangeKey,
  filterObservationRange,
  formatObservedOn,
  formatValue,
  getAvailableTrendRanges,
  projectRelativeChangeSeries,
} from "./dataset-detail-view-model";

interface ObservationsChartProps {
  observations: ObservationPoint[];
  onRelativeSettingsChange?: (settings: RelativeChangeSettings) => void;
  unitLabel?: string | null | undefined;
  unitType?: string | null | undefined;
  relativeSettings?: RelativeChangeSettings;
  selectedRange?: TrendRangeKey;
  onRangeChange?: (range: TrendRangeKey) => void;
}

interface ObservationChartPoint {
  baselineObservedOn?: string | null;
  changePercent: number | null;
  changeValue: number | null;
  computability?: string;
  date: string;
  dateLabel: string;
  value: number;
  valueLabel: string;
}

interface ObservationTooltipContentProps {
  active?: boolean;
  payload?: Array<{
    payload?: ObservationChartPoint;
  }>;
}

const CHART_MIN_HEIGHT = 288;
const CHART_MAX_HEIGHT = 360;
const CHART_ASPECT_RATIO = 0.54;
const CHART_DEFAULT_WIDTH = 640;
const Y_AXIS_MIN_PADDING_RATIO = 0.05;
const Y_AXIS_FALLBACK_PADDING = 1;

const formatSignedNumber = (value: number, maximumFractionDigits: number): string => {
  const abs = Math.abs(value);
  const sign = value > 0 ? "+" : value < 0 ? "-" : "";
  return `${sign}${new Intl.NumberFormat("en-US", {
    maximumFractionDigits,
    minimumFractionDigits: maximumFractionDigits,
  }).format(abs)}`;
};

const formatAxisNumber = (value: number): string => {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0,
  }).format(value);
};

const formatPercentValue = (value: number): string => {
  return `${formatSignedNumber(value, 3)}%`;
};

const parseNumericControl = (value: string): number => {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : 0;
};

const toChartData = (
  observations: ObservationPoint[],
  unitType?: string | null,
  unitLabel?: string | null,
): ObservationChartPoint[] => {
  return observations.map((observation, index) => {
    const previous = index > 0 ? observations[index - 1] : null;
    const changeValue = previous ? observation.value - previous.value : null;
    const changePercent =
      previous && previous.value !== 0 && changeValue !== null
        ? (changeValue / previous.value) * 100
        : null;

    return {
      changePercent,
      changeValue,
      computability: "computable",
      date: observation.observed_on,
      dateLabel: formatObservedOn(observation.observed_on),
      value: observation.value,
      valueLabel: formatValue(observation.value, unitType, unitLabel),
    };
  });
};

const toRelativeChartData = (
  observations: ObservationPoint[],
  settings: RelativeChangeSettings,
): {
  availableDates: string[];
  chartData: ObservationChartPoint[];
  hasComputablePoints: boolean;
  selectedFixedBaselineDate: string | null;
} => {
  const projection = projectRelativeChangeSeries(observations, settings);
  const baselineStartIndex =
    settings.baselineMode === "fixed" && projection.selectedFixedBaselineDate
      ? projection.points.findIndex(
          (point) => point.observed_on === projection.selectedFixedBaselineDate,
        )
      : -1;
  const projectedPoints =
    baselineStartIndex >= 0 ? projection.points.slice(baselineStartIndex) : projection.points;

  return {
    availableDates: projection.availableDates,
    chartData: projectedPoints.map((point) => {
      const valueLabel = point.value === null ? "Unavailable" : formatPercentValue(point.value);

      return {
        baselineObservedOn: point.baselineObservedOn,
        changePercent: null,
        changeValue: point.value,
        computability: point.computability,
        date: point.observed_on,
        dateLabel: formatObservedOn(point.observed_on),
        value: point.value ?? Number.NaN,
        valueLabel,
      };
    }),
    hasComputablePoints: projection.hasComputablePoints,
    selectedFixedBaselineDate: projection.selectedFixedBaselineDate,
  };
};

const getYAxisDomain = (chartData: ObservationChartPoint[]): [number, number] => {
  const values = chartData.map((point) => point.value).filter((value) => Number.isFinite(value));

  if (values.length === 0) {
    return [0, 1];
  }

  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const spread = maxValue - minValue;
  const padding =
    spread === 0
      ? Math.max(Math.abs(maxValue) * Y_AXIS_MIN_PADDING_RATIO, Y_AXIS_FALLBACK_PADDING)
      : spread * Y_AXIS_MIN_PADDING_RATIO;

  return [minValue - padding, maxValue + padding];
};

const ObservationsChartTooltip = ({
  active,
  payload,
}: ObservationTooltipContentProps): JSX.Element | null => {
  if (!active || !payload?.length || !payload[0]?.payload) {
    return null;
  }

  const point = payload[0].payload;
  if (point.computability && point.computability !== "computable") {
    return (
      <div className="min-w-48 rounded-[1.15rem] bg-[color-mix(in_srgb,var(--shell-background)_96%,#ffffff)] px-5 py-4 shadow-[0_18px_50px_rgba(15,23,42,0.14)] ring-1 ring-[color-mix(in_srgb,var(--shell-border)_82%,transparent)] backdrop-blur-sm">
        <p className="m-0 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-(--shell-muted) text-[1.05rem] italic">
          {point.dateLabel}
        </p>
        <p className="mt-3 text-(--shell-muted) text-[0.95rem]">Relative value unavailable</p>
      </div>
    );
  }

  const isPositive = (point.changeValue ?? 0) > 0;
  const isNegative = (point.changeValue ?? 0) < 0;
  const isRelativeModePoint = Boolean(point.baselineObservedOn) && point.changePercent === null;
  const movementClass = isPositive
    ? "text-emerald-700 dark:text-emerald-300"
    : isNegative
      ? "text-rose-700 dark:text-rose-300"
      : "text-(--shell-muted)";

  return (
    <div className="min-w-48 rounded-[1.15rem] bg-[color-mix(in_srgb,var(--shell-background)_96%,#ffffff)] px-5 py-4 shadow-[0_18px_50px_rgba(15,23,42,0.14)] ring-1 ring-[color-mix(in_srgb,var(--shell-border)_82%,transparent)] backdrop-blur-sm">
      <p className="m-0 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-(--shell-muted) text-[1.05rem] italic">
        {point.dateLabel}
      </p>
      <div className="mt-4 h-px w-16 bg-(--shell-border)" />
      <p className="mt-5 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-(--shell-foreground) text-[2.4rem] leading-none">
        {point.valueLabel}
      </p>
      {isRelativeModePoint ? (
        <p className={`mt-3 font-semibold text-[1.05rem] ${movementClass}`}>
          {`Relative to ${point.baselineObservedOn}`}
        </p>
      ) : null}
      {point.changeValue !== null && point.changePercent !== null ? (
        <p className={`mt-3 font-semibold text-[1.05rem] ${movementClass}`}>
          {`${formatSignedNumber(point.changeValue, 3)} (${formatSignedNumber(point.changePercent, 2)}%)`}
        </p>
      ) : (
        <p className="mt-3 text-(--shell-muted) text-[0.95rem]">No prior observation</p>
      )}
    </div>
  );
};

export const ObservationsChart = ({
  observations,
  onRelativeSettingsChange,
  unitLabel,
  unitType,
  relativeSettings,
  selectedRange,
  onRangeChange,
}: ObservationsChartProps): JSX.Element => {
  const availableRanges = getAvailableTrendRanges(observations);
  const [internalRange, setInternalRange] = React.useState<TrendRangeKey>("ALL");
  const [internalRelativeSettings, setInternalRelativeSettings] =
    React.useState<RelativeChangeSettings>(DEFAULT_RELATIVE_CHANGE_SETTINGS);
  const [chartWidth, setChartWidth] = React.useState(CHART_DEFAULT_WIDTH);
  const chartContainerRef = React.useRef<HTMLDivElement | null>(null);
  const preferredRange = selectedRange ?? internalRange;
  const activeRange = availableRanges.includes(preferredRange) ? preferredRange : "ALL";
  const settings = relativeSettings ?? internalRelativeSettings;
  const isFixedBaselineActive =
    settings.valueMode === "relative" && settings.baselineMode === "fixed";

  if (observations.length === 0) {
    return <EmptyState message="No observation data available" />;
  }

  const filtered = isFixedBaselineActive
    ? observations
    : filterObservationRange(observations, activeRange);
  const {
    availableDates: relativeAvailableDates,
    chartData: relativeChartData,
    hasComputablePoints,
    selectedFixedBaselineDate,
  } = toRelativeChartData(filtered, settings);
  const chartData =
    settings.valueMode === "relative"
      ? relativeChartData
      : toChartData(filtered, unitType, unitLabel);
  const yAxisDomain = getYAxisDomain(chartData);
  const chartHeight = Math.max(
    CHART_MIN_HEIGHT,
    Math.min(CHART_MAX_HEIGHT, Math.round(chartWidth * CHART_ASPECT_RATIO)),
  );

  const handleRangeChange = (range: TrendRangeKey): void => {
    if (onRangeChange) {
      onRangeChange(range);
      return;
    }
    setInternalRange(range);
  };

  const updateRelativeSettings = (next: Partial<RelativeChangeSettings>): void => {
    const resolved = { ...settings, ...next };

    if (onRelativeSettingsChange) {
      onRelativeSettingsChange(resolved);
      return;
    }

    setInternalRelativeSettings(resolved);
  };

  const maxOffset = Math.max(0, filtered.length - 1);
  const rollingOffsetCandidates = [1, 2, 3, 6, 12, 24]
    .filter((value) => value <= maxOffset)
    .concat(settings.rollingOffset)
    .filter((value, index, values) => value > 0 && values.indexOf(value) === index)
    .sort((left, right) => left - right);

  const fixedOffsetCandidates = [1, 2, 3, 6, 12, 24]
    .filter((value) => value <= maxOffset)
    .concat(settings.fixedBaselineOffset)
    .filter((value, index, values) => value >= 0 && values.indexOf(value) === index)
    .sort((left, right) => left - right);

  const fixedDateOptions = settings.fixedBaselineDate
    ? [...new Set([settings.fixedBaselineDate, ...relativeAvailableDates])]
    : relativeAvailableDates;

  const showRelativeUnavailableState = settings.valueMode === "relative" && !hasComputablePoints;

  React.useEffect(() => {
    const container = chartContainerRef.current;
    if (!container) {
      return;
    }

    const updateWidth = (): void => {
      const nextWidth = container.getBoundingClientRect().width;
      setChartWidth(nextWidth > 0 ? nextWidth : CHART_DEFAULT_WIDTH);
    };

    updateWidth();

    const resizeObserver = new ResizeObserver(() => {
      updateWidth();
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  return (
    <div
      aria-label="Time series chart"
      className="flex h-full min-h-80 min-w-0 flex-col bg-(--shell-surface) pt-1"
      data-testid="observations-chart"
    >
      {availableRanges.length > 1 ? (
        <div
          className="mb-[0.7rem] flex flex-wrap justify-end gap-[0.35rem]"
          data-testid="observations-chart-controls"
        >
          {availableRanges.map((range) => (
            <button
              aria-pressed={activeRange === range}
              className={`cursor-pointer border border-(--shell-border) bg-(--shell-surface) px-[0.52rem] py-[0.2rem] text-[0.68rem] tracking-[0.06em] aria-pressed:border-(--shell-foreground) aria-pressed:bg-(--shell-foreground) aria-pressed:text-(--shell-surface) ${isFixedBaselineActive ? "cursor-not-allowed opacity-45" : ""}`}
              disabled={isFixedBaselineActive}
              key={range}
              onClick={() => {
                if (isFixedBaselineActive) {
                  return;
                }
                handleRangeChange(range);
              }}
              type="button"
            >
              {range}
            </button>
          ))}
        </div>
      ) : null}
      <div className="mb-[0.7rem] flex flex-wrap items-center justify-between gap-2">
        <div
          className="flex flex-wrap gap-[0.35rem]"
          data-testid="observations-chart-mode-controls"
        >
          <button
            aria-pressed={settings.valueMode === "observed"}
            className="cursor-pointer border border-(--shell-border) bg-(--shell-surface) px-[0.52rem] py-[0.2rem] text-[0.68rem] tracking-[0.06em] aria-pressed:border-(--shell-foreground) aria-pressed:bg-(--shell-foreground) aria-pressed:text-(--shell-surface)"
            onClick={() => {
              updateRelativeSettings({ valueMode: "observed" });
            }}
            type="button"
          >
            Observed
          </button>
          <button
            aria-pressed={settings.valueMode === "relative"}
            className="cursor-pointer border border-(--shell-border) bg-(--shell-surface) px-[0.52rem] py-[0.2rem] text-[0.68rem] tracking-[0.06em] aria-pressed:border-(--shell-foreground) aria-pressed:bg-(--shell-foreground) aria-pressed:text-(--shell-surface)"
            onClick={() => {
              updateRelativeSettings({ valueMode: "relative" });
            }}
            type="button"
          >
            Relative %
          </button>
        </div>

        {settings.valueMode === "relative" ? (
          <div
            className="flex flex-wrap items-center gap-[0.4rem]"
            data-testid="observations-chart-relative-controls"
          >
            <select
              aria-label="Relative baseline mode"
              className="border border-(--shell-border) bg-(--shell-surface) px-2 py-1 text-[0.72rem]"
              onChange={(event) => {
                updateRelativeSettings({
                  baselineMode: event.target.value as RelativeChangeSettings["baselineMode"],
                });
              }}
              value={settings.baselineMode}
            >
              <option value="rolling">Rolling baseline</option>
              <option value="fixed">Fixed baseline</option>
            </select>

            {settings.baselineMode === "rolling" ? (
              <select
                aria-label="Rolling offset"
                className="border border-(--shell-border) bg-(--shell-surface) px-2 py-1 text-[0.72rem]"
                onChange={(event) => {
                  updateRelativeSettings({
                    rollingOffset: parseNumericControl(event.target.value),
                  });
                }}
                value={settings.rollingOffset}
              >
                {rollingOffsetCandidates.map((offset) => (
                  <option key={offset} value={offset}>
                    {`${offset} observations ago`}
                  </option>
                ))}
              </select>
            ) : (
              <>
                <select
                  aria-label="Fixed baseline source"
                  className="border border-(--shell-border) bg-(--shell-surface) px-2 py-1 text-[0.72rem]"
                  onChange={(event) => {
                    updateRelativeSettings({
                      fixedSelectionMode: event.target
                        .value as RelativeChangeSettings["fixedSelectionMode"],
                    });
                  }}
                  value={settings.fixedSelectionMode}
                >
                  <option value="date">By date</option>
                  <option value="offset">By offset</option>
                </select>
                {settings.fixedSelectionMode === "date" ? (
                  <select
                    aria-label="Fixed baseline date"
                    className="border border-(--shell-border) bg-(--shell-surface) px-2 py-1 text-[0.72rem]"
                    onChange={(event) => {
                      updateRelativeSettings({ fixedBaselineDate: event.target.value });
                    }}
                    value={settings.fixedBaselineDate ?? ""}
                  >
                    {!settings.fixedBaselineDate ? (
                      <option value="">Select baseline date</option>
                    ) : null}
                    {fixedDateOptions.map((date) => (
                      <option key={date} value={date}>
                        {date}
                      </option>
                    ))}
                  </select>
                ) : (
                  <select
                    aria-label="Fixed baseline offset"
                    className="border border-(--shell-border) bg-(--shell-surface) px-2 py-1 text-[0.72rem]"
                    onChange={(event) => {
                      updateRelativeSettings({
                        fixedBaselineOffset: parseNumericControl(event.target.value),
                      });
                    }}
                    value={settings.fixedBaselineOffset}
                  >
                    {fixedOffsetCandidates.map((offset) => (
                      <option key={offset} value={offset}>
                        {`${offset} observations ago`}
                      </option>
                    ))}
                  </select>
                )}
              </>
            )}
          </div>
        ) : null}
      </div>

      {showRelativeUnavailableState ? (
        <p
          className="mb-2 text-(--shell-muted) text-[0.78rem]"
          data-testid="relative-change-unavailable"
        >
          Selected baseline is unavailable for the current scope.
        </p>
      ) : null}
      {isFixedBaselineActive && selectedFixedBaselineDate ? (
        <p className="mb-2 text-(--shell-muted) text-[0.78rem]" data-testid="fixed-baseline-note">
          Chart starts at selected baseline observation.
        </p>
      ) : null}
      <div className="w-full min-w-0 flex-1" ref={chartContainerRef}>
        <LineChart
          data={chartData}
          height={chartHeight}
          margin={{ bottom: 18, left: 8, right: 8, top: 8 }}
          width={chartWidth}
        >
          <XAxis dataKey="date" minTickGap={32} tickMargin={14} />
          <YAxis
            domain={yAxisDomain}
            tickFormatter={(value: number) =>
              settings.valueMode === "relative"
                ? `${formatAxisNumber(value)}%`
                : formatAxisNumber(value)
            }
          />
          <Tooltip content={<ObservationsChartTooltip />} cursor={false} />
          <Line
            dataKey="value"
            dot={false}
            stroke="var(--shell-foreground)"
            strokeWidth={2.25}
            type="monotone"
          />
        </LineChart>
      </div>
    </div>
  );
};
