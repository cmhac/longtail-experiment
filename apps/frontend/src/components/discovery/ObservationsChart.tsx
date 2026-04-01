"use client";

import React from "react";
import type { JSX } from "react";
import { Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import type { ObservationPoint, TrendVisualizationSpan } from "../../lib/api/discovery-types";
import { TrendTooltipController } from "../trends/TrendTooltipController";
import { EmptyState } from "./EmptyState";
import { ChartComboControl, type ChartComboOption } from "./chart-controls/ChartComboControl";
import { ChartToggleGroup } from "./chart-controls/ChartToggleGroup";
import {
  ChartTooltipDate,
  ChartTooltipDivider,
  ChartTooltipRoot,
  ChartTooltipText,
  ChartTooltipValue,
} from "./chart-controls/ChartTooltip";
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
import { useInfiniteScrollObserver } from "./useInfiniteScrollObserver";

interface ObservationsChartProps {
  observations: ObservationPoint[];
  trendSpans?: TrendVisualizationSpan[];
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

const COMBOBOX_PAGE_SIZE = 24;

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

const sortObservationDatesDesc = (dates: string[]): string[] => {
  return [...dates].sort((left, right) => {
    const leftTime = Date.parse(`${left}T00:00:00Z`);
    const rightTime = Date.parse(`${right}T00:00:00Z`);
    if (Number.isFinite(leftTime) && Number.isFinite(rightTime)) {
      return rightTime - leftTime;
    }

    return right.localeCompare(left);
  });
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
      <ChartTooltipRoot>
        <ChartTooltipDate>{point.dateLabel}</ChartTooltipDate>
        <ChartTooltipText>Relative value unavailable</ChartTooltipText>
      </ChartTooltipRoot>
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
    <ChartTooltipRoot>
      <ChartTooltipDate>{point.dateLabel}</ChartTooltipDate>
      <ChartTooltipDivider />
      <ChartTooltipValue>{point.valueLabel}</ChartTooltipValue>
      {isRelativeModePoint ? (
        <ChartTooltipText className={`mt-3 font-semibold text-[1.05rem] ${movementClass}`}>
          {`Relative to ${point.baselineObservedOn}`}
        </ChartTooltipText>
      ) : null}
      {point.changeValue !== null && point.changePercent !== null ? (
        <ChartTooltipText className={`mt-3 font-semibold text-[1.05rem] ${movementClass}`}>
          {`${formatSignedNumber(point.changeValue, 3)} (${formatSignedNumber(point.changePercent, 2)}%)`}
        </ChartTooltipText>
      ) : (
        <ChartTooltipText>No prior observation</ChartTooltipText>
      )}
    </ChartTooltipRoot>
  );
};

export const ObservationsChart = ({
  observations,
  trendSpans = [],
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
  const [baselineModeInput, setBaselineModeInput] = React.useState("");
  const [rollingOffsetInput, setRollingOffsetInput] = React.useState("");
  const [fixedDateInput, setFixedDateInput] = React.useState("");
  const [fixedDateLoadingMore, setFixedDateLoadingMore] = React.useState(false);
  const [fixedDateVisibleCount, setFixedDateVisibleCount] = React.useState(COMBOBOX_PAGE_SIZE);
  const chartContainerRef = React.useRef<HTMLDivElement | null>(null);
  const fixedDateListContainerRef = React.useRef<HTMLDivElement | null>(null);
  const fixedDateLoadTimerRef = React.useRef<number | null>(null);
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
  const chartDates = chartData.map((point) => point.date);
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

  const fixedDateOptions = settings.fixedBaselineDate
    ? [...new Set([settings.fixedBaselineDate, ...relativeAvailableDates])]
    : relativeAvailableDates;
  const sortedFixedDateOptions = sortObservationDatesDesc(fixedDateOptions);
  const normalizedFixedDateInput = fixedDateInput.trim().toLowerCase();
  const normalizedSelectedFixedDate = (settings.fixedBaselineDate ?? "").trim().toLowerCase();
  const shouldFilterFixedDates =
    normalizedFixedDateInput.length > 0 && normalizedFixedDateInput !== normalizedSelectedFixedDate;
  const canPaginateFixedDates =
    settings.valueMode === "relative" &&
    settings.baselineMode === "fixed" &&
    !shouldFilterFixedDates;
  const hasMoreFixedDates =
    canPaginateFixedDates && fixedDateVisibleCount < sortedFixedDateOptions.length;

  const loadMoreFixedDates = React.useCallback(() => {
    if (!hasMoreFixedDates || fixedDateLoadingMore) {
      return;
    }

    setFixedDateLoadingMore(true);
    if (fixedDateLoadTimerRef.current !== null) {
      window.clearTimeout(fixedDateLoadTimerRef.current);
    }

    fixedDateLoadTimerRef.current = window.setTimeout(() => {
      setFixedDateVisibleCount((value) => value + COMBOBOX_PAGE_SIZE);
      setFixedDateLoadingMore(false);
      fixedDateLoadTimerRef.current = null;
    }, 100);
  }, [fixedDateLoadingMore, hasMoreFixedDates]);

  React.useEffect(() => {
    return () => {
      if (fixedDateLoadTimerRef.current !== null) {
        window.clearTimeout(fixedDateLoadTimerRef.current);
      }
    };
  }, []);

  const fixedDateSentinelRef = useInfiniteScrollObserver({
    enabled: hasMoreFixedDates && !fixedDateLoadingMore,
    onIntersect: loadMoreFixedDates,
    rootRef: fixedDateListContainerRef,
    rootMargin: "0px 0px 80px 0px",
  });

  React.useEffect(() => {
    setBaselineModeInput(
      settings.baselineMode === "rolling" ? "Rolling baseline" : "Fixed baseline",
    );
  }, [settings.baselineMode]);

  React.useEffect(() => {
    setRollingOffsetInput(`${settings.rollingOffset} observations ago`);
  }, [settings.rollingOffset]);

  React.useEffect(() => {
    setFixedDateInput(settings.fixedBaselineDate ?? "");
    setFixedDateLoadingMore(false);
    setFixedDateVisibleCount(COMBOBOX_PAGE_SIZE);
  }, [settings.fixedBaselineDate]);

  const showRelativeUnavailableState = settings.valueMode === "relative" && !hasComputablePoints;

  const baselineModeOptions: ChartComboOption[] = [
    { label: "Rolling baseline", value: "rolling" },
    { label: "Fixed baseline", value: "fixed" },
  ];

  const rollingOffsetOptions: ChartComboOption[] = rollingOffsetCandidates.map((offset) => ({
    label: `${offset} observations ago`,
    value: String(offset),
  }));

  const fixedDateControlOptions: ChartComboOption[] = [
    { label: "Select baseline date", value: "" },
    ...sortedFixedDateOptions.map((date) => ({
      label: date,
      value: date,
    })),
  ];

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
        <ChartToggleGroup
          activeValue={activeRange}
          className="mb-[0.7rem] flex flex-wrap justify-end gap-[0.35rem]"
          disabled={isFixedBaselineActive}
          onChange={handleRangeChange}
          options={availableRanges.map((range) => ({
            label: range,
            value: range,
          }))}
          testId="observations-chart-controls"
        />
      ) : null}
      <div className="mb-[0.7rem] flex flex-wrap items-center justify-between gap-2">
        <ChartToggleGroup
          activeValue={settings.valueMode}
          className="flex flex-wrap gap-[0.35rem]"
          onChange={(value) => {
            updateRelativeSettings({ valueMode: value });
          }}
          options={[
            {
              label: "Observed",
              value: "observed",
            },
            {
              label: "Relative %",
              value: "relative",
            },
          ]}
          testId="observations-chart-mode-controls"
        />

        {settings.valueMode === "relative" ? (
          <div
            className="flex flex-nowrap items-center gap-[0.4rem] overflow-x-auto"
            data-testid="observations-chart-relative-controls"
          >
            <ChartComboControl
              className="w-37 min-w-32"
              inputValue={baselineModeInput}
              label="Relative baseline mode"
              emptyLabel="No baseline modes"
              onInputChange={setBaselineModeInput}
              onSelect={(value) => {
                updateRelativeSettings({
                  baselineMode: value as RelativeChangeSettings["baselineMode"],
                });
              }}
              options={baselineModeOptions}
              selectedValue={settings.baselineMode}
              testId="relative-baseline-mode-control"
            />

            {settings.baselineMode === "rolling" ? (
              <ChartComboControl
                className="w-37 min-w-32"
                emptyLabel="No matching offsets"
                inputValue={rollingOffsetInput}
                label="Rolling offset"
                onInputChange={setRollingOffsetInput}
                onSelect={(value) => {
                  updateRelativeSettings({
                    rollingOffset: parseNumericControl(value),
                  });
                }}
                options={rollingOffsetOptions}
                selectedValue={String(settings.rollingOffset)}
                testId="rolling-offset-control"
              />
            ) : (
              <ChartComboControl
                className="w-37 min-w-32"
                emptyLabel="No matching dates"
                infiniteScrollRef={fixedDateSentinelRef}
                inputValue={fixedDateInput}
                isInfiniteLoading={fixedDateLoadingMore}
                label="Fixed baseline date"
                listContainerRef={fixedDateListContainerRef}
                onInputChange={(value) => {
                  setFixedDateInput(value);
                  setFixedDateLoadingMore(false);
                  setFixedDateVisibleCount(COMBOBOX_PAGE_SIZE);
                }}
                onSelect={(value) => {
                  updateRelativeSettings({ fixedBaselineDate: value === "" ? null : value });
                }}
                options={fixedDateControlOptions}
                paginated
                selectedValue={settings.fixedBaselineDate ?? ""}
                testId="fixed-baseline-date-control"
                visibleCount={fixedDateVisibleCount}
              />
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
      <div className="relative w-full min-w-0 flex-1" ref={chartContainerRef}>
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
        {settings.valueMode === "observed" ? (
          <TrendTooltipController chartDates={chartDates} spans={trendSpans} />
        ) : null}
      </div>
    </div>
  );
};
