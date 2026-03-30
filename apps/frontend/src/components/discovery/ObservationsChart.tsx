"use client";

import { ComboBox, Input, ListBox, ListBoxItem, Spinner } from "@heroui/react";
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
import { useInfiniteScrollObserver } from "./useInfiniteScrollObserver";

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

interface ComboBoxOption {
  label: string;
  value: string;
}

const COMBOBOX_PAGE_SIZE = 24;
const NO_MATCH_VALUE = "__no_match__";

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
  const [baselineModeInput, setBaselineModeInput] = React.useState("");
  const [rollingOffsetInput, setRollingOffsetInput] = React.useState("");
  const [fixedSourceInput, setFixedSourceInput] = React.useState("");
  const [fixedDateInput, setFixedDateInput] = React.useState("");
  const [fixedOffsetInput, setFixedOffsetInput] = React.useState("");
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
  const sortedFixedDateOptions = sortObservationDatesDesc(fixedDateOptions);
  const normalizedFixedDateInput = fixedDateInput.trim().toLowerCase();
  const normalizedSelectedFixedDate = (settings.fixedBaselineDate ?? "").trim().toLowerCase();
  const shouldFilterFixedDates =
    normalizedFixedDateInput.length > 0 && normalizedFixedDateInput !== normalizedSelectedFixedDate;
  const canPaginateFixedDates =
    settings.valueMode === "relative" &&
    settings.baselineMode === "fixed" &&
    settings.fixedSelectionMode === "date" &&
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
    setFixedSourceInput(settings.fixedSelectionMode === "date" ? "By date" : "By offset");
    setFixedDateLoadingMore(false);
    setFixedDateVisibleCount(COMBOBOX_PAGE_SIZE);
  }, [settings.fixedSelectionMode]);

  React.useEffect(() => {
    setFixedDateInput(settings.fixedBaselineDate ?? "");
  }, [settings.fixedBaselineDate]);

  React.useEffect(() => {
    setFixedOffsetInput(`${settings.fixedBaselineOffset} observations ago`);
  }, [settings.fixedBaselineOffset]);

  const renderControlComboBox = ({
    emptyLabel,
    infiniteScrollRef,
    inputValue,
    isInfiniteLoading,
    label,
    listContainerRef,
    onInputChange,
    onSelect,
    options,
    paginated,
    selectedValue,
    testId,
  }: {
    emptyLabel?: string;
    infiniteScrollRef?: React.RefObject<HTMLDivElement | null>;
    inputValue: string;
    isInfiniteLoading?: boolean;
    label: string;
    listContainerRef?: React.RefObject<HTMLDivElement | null>;
    onInputChange?: (value: string) => void;
    onSelect: (value: string) => void;
    options: ComboBoxOption[];
    paginated?: boolean;
    selectedValue: string;
    testId: string;
  }): JSX.Element => {
    const normalizedInput = inputValue.trim().toLowerCase();
    const selectedOption = options.find((option) => option.value === selectedValue);
    const normalizedSelectedLabel = selectedOption?.label.trim().toLowerCase() ?? "";
    const shouldFilter = normalizedInput.length > 0 && normalizedInput !== normalizedSelectedLabel;
    const filteredOptions = !shouldFilter
      ? options
      : options.filter((option) => option.label.toLowerCase().includes(normalizedInput));
    const visibleOptions =
      paginated && !shouldFilter
        ? (() => {
            const pagedOptions = filteredOptions.slice(0, fixedDateVisibleCount);
            if (
              !selectedOption ||
              pagedOptions.some((option) => option.value === selectedOption.value)
            ) {
              return pagedOptions;
            }

            return [selectedOption, ...pagedOptions];
          })()
        : filteredOptions;
    const hasMore =
      Boolean(paginated) && !shouldFilter && filteredOptions.length > visibleOptions.length;
    const renderedOptions =
      visibleOptions.length > 0
        ? visibleOptions
        : [{ label: emptyLabel ?? "No matching options", value: NO_MATCH_VALUE }];

    return (
      <ComboBox
        aria-label={label}
        className="w-[9.25rem] min-w-[8rem]"
        data-testid={testId}
        inputValue={inputValue}
        items={renderedOptions}
        onInputChange={onInputChange ?? (() => {})}
        onSelectionChange={(key) => {
          if (typeof key === "string") {
            if (key === NO_MATCH_VALUE) {
              return;
            }
            onSelect(key);
          }
        }}
        selectedKey={selectedValue}
      >
        <ComboBox.InputGroup className="box-border overflow-hidden rounded-[0.8rem] border border-(--shell-border) bg-(--shell-surface) transition-[border-width,border-color] duration-150 focus-within:border-(--shell-foreground) focus-within:border-2 focus-within:ring-0">
          <Input className="min-h-8 truncate border-0 bg-transparent py-[0.28rem] pr-[2.15rem] pl-[0.45rem] text-(--shell-foreground) outline-none focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0" />
          <ComboBox.Trigger
            aria-label={`Open ${label} options`}
            className="min-w-[2.15rem] px-[0.45rem] text-(--shell-muted)"
          />
        </ComboBox.InputGroup>
        <ComboBox.Popover className="rounded-[0.8rem] border border-(--shell-border) bg-(--shell-surface)">
          <div className="max-h-56 overflow-y-auto" ref={listContainerRef}>
            <ListBox>
              {renderedOptions.map((option) => (
                <ListBoxItem
                  className="text-(--shell-foreground) data-[focused=true]:bg-(--shell-background) data-[hovered=true]:bg-(--shell-background) data-[selected=true]:bg-(--shell-background) data-[focused=true]:text-(--shell-foreground) data-[hovered=true]:text-(--shell-foreground) data-[selected=true]:text-(--shell-foreground)"
                  id={option.value}
                  key={option.value}
                  textValue={option.label}
                >
                  {option.label}
                </ListBoxItem>
              ))}
            </ListBox>
            {hasMore ? (
              <div
                className="h-2 w-full"
                data-testid={`${testId}-infinite-sentinel`}
                ref={infiniteScrollRef}
              />
            ) : null}
            {isInfiniteLoading ? (
              <div className="flex justify-center py-2" data-testid={`${testId}-infinite-loading`}>
                <Spinner color="current" size="sm" style={{ color: "var(--foreground)" }} />
              </div>
            ) : null}
          </div>
        </ComboBox.Popover>
      </ComboBox>
    );
  };

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
            className="flex flex-nowrap items-center gap-[0.4rem] overflow-x-auto"
            data-testid="observations-chart-relative-controls"
          >
            {renderControlComboBox({
              inputValue: baselineModeInput,
              label: "Relative baseline mode",
              onInputChange: setBaselineModeInput,
              onSelect: (value) => {
                updateRelativeSettings({
                  baselineMode: value as RelativeChangeSettings["baselineMode"],
                });
              },
              options: [
                { label: "Rolling baseline", value: "rolling" },
                { label: "Fixed baseline", value: "fixed" },
              ],
              emptyLabel: "No baseline modes",
              selectedValue: settings.baselineMode,
              testId: "relative-baseline-mode-control",
            })}

            {settings.baselineMode === "rolling" ? (
              renderControlComboBox({
                inputValue: rollingOffsetInput,
                label: "Rolling offset",
                onInputChange: setRollingOffsetInput,
                onSelect: (value) => {
                  updateRelativeSettings({
                    rollingOffset: parseNumericControl(value),
                  });
                },
                options: rollingOffsetCandidates.map((offset) => ({
                  label: `${offset} observations ago`,
                  value: String(offset),
                })),
                emptyLabel: "No matching offsets",
                selectedValue: String(settings.rollingOffset),
                testId: "rolling-offset-control",
              })
            ) : (
              <>
                {renderControlComboBox({
                  inputValue: fixedSourceInput,
                  label: "Fixed baseline source",
                  onInputChange: setFixedSourceInput,
                  onSelect: (value) => {
                    updateRelativeSettings({
                      fixedSelectionMode: value as RelativeChangeSettings["fixedSelectionMode"],
                    });
                  },
                  options: [
                    { label: "By date", value: "date" },
                    { label: "By offset", value: "offset" },
                  ],
                  emptyLabel: "No baseline sources",
                  selectedValue: settings.fixedSelectionMode,
                  testId: "fixed-baseline-source-control",
                })}
                {settings.fixedSelectionMode === "date"
                  ? renderControlComboBox({
                      infiniteScrollRef: fixedDateSentinelRef,
                      inputValue: fixedDateInput,
                      isInfiniteLoading: fixedDateLoadingMore,
                      label: "Fixed baseline date",
                      listContainerRef: fixedDateListContainerRef,
                      onInputChange: (value) => {
                        setFixedDateInput(value);
                        setFixedDateLoadingMore(false);
                        setFixedDateVisibleCount(COMBOBOX_PAGE_SIZE);
                      },
                      onSelect: (value) => {
                        updateRelativeSettings({ fixedBaselineDate: value === "" ? null : value });
                      },
                      options: [
                        { label: "Select baseline date", value: "" },
                        ...sortedFixedDateOptions.map((date) => ({
                          label: date,
                          value: date,
                        })),
                      ],
                      emptyLabel: "No matching dates",
                      paginated: true,
                      selectedValue: settings.fixedBaselineDate ?? "",
                      testId: "fixed-baseline-date-control",
                    })
                  : renderControlComboBox({
                      inputValue: fixedOffsetInput,
                      label: "Fixed baseline offset",
                      onInputChange: setFixedOffsetInput,
                      onSelect: (value) => {
                        updateRelativeSettings({
                          fixedBaselineOffset: parseNumericControl(value),
                        });
                      },
                      options: fixedOffsetCandidates.map((offset) => ({
                        label: `${offset} observations ago`,
                        value: String(offset),
                      })),
                      emptyLabel: "No matching offsets",
                      selectedValue: String(settings.fixedBaselineOffset),
                      testId: "fixed-baseline-offset-control",
                    })}
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
