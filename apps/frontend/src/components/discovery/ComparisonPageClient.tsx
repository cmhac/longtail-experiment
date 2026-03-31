"use client";

import { Button, Card, Input, Label, ListBox, Select } from "@heroui/react";
import React, { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchDatasetDetail } from "../../lib/api/discovery-client";
import type { DatasetDetail } from "../../lib/api/discovery-types";
import {
  COMPARISON_STATE_EVENT,
  ComparisonStateCorruptedError,
  getComparisonLineColor,
  getComparisonState,
  isComparisonSelectionCompatible,
  removeComparisonDataset,
  resetComparisonState,
  setComparisonChartSettings,
} from "./comparison-state";

interface ChartRow {
  date: string;
  [datasetId: string]: number | string | null;
}

interface SeriesBaseline {
  baselineDate: string | null;
  baselineValue: number | null;
}

export const parseDate = (value: string): number => Date.parse(`${value}T00:00:00Z`);

export const resolveFixedBaseline = (
  observations: DatasetDetail["observations"],
  fixedBaselineDate: string | null,
): SeriesBaseline => {
  if (!fixedBaselineDate || observations.length === 0) {
    return { baselineDate: null, baselineValue: null };
  }

  const sorted = [...observations].sort(
    (left, right) => parseDate(left.observed_on) - parseDate(right.observed_on),
  );
  const fixedTime = parseDate(fixedBaselineDate);

  const exact = sorted.find((point) => point.observed_on === fixedBaselineDate);
  if (exact) {
    return { baselineDate: exact.observed_on, baselineValue: exact.value };
  }

  const priorPoints = sorted.filter((point) => parseDate(point.observed_on) <= fixedTime);
  const nearestPrior = priorPoints.at(-1);
  if (nearestPrior) {
    return { baselineDate: nearestPrior.observed_on, baselineValue: nearestPrior.value };
  }

  const nearestAny = sorted.reduce<DatasetDetail["observations"][number] | null>(
    (closest, point) => {
      if (!closest) {
        return point;
      }

      const pointDelta = Math.abs(parseDate(point.observed_on) - fixedTime);
      const closestDelta = Math.abs(parseDate(closest.observed_on) - fixedTime);
      return pointDelta < closestDelta ? point : closest;
    },
    null,
  );

  if (!nearestAny) {
    return { baselineDate: null, baselineValue: null };
  }

  return { baselineDate: nearestAny.observed_on, baselineValue: nearestAny.value };
};

export const buildChartRows = (
  datasets: DatasetDetail[],
  valueMode: "observed" | "relative",
  baselineMode: "rolling" | "fixed",
  rollingOffset: number,
  fixedBaselineDate: string | null,
): ChartRow[] => {
  const allDates = new Set<string>();
  for (const dataset of datasets) {
    for (const point of dataset.observations) {
      allDates.add(point.observed_on);
    }
  }

  const orderedDates = [...allDates].sort((left, right) => parseDate(left) - parseDate(right));

  const lookup = new Map<string, Map<string, number>>();
  const rollingBaselineLookup = new Map<string, Map<string, number | null>>();

  for (const dataset of datasets) {
    const seriesMap = new Map<string, number>();
    const rollingBaseline = new Map<string, number | null>();
    const sorted = [...dataset.observations].sort(
      (left, right) => parseDate(left.observed_on) - parseDate(right.observed_on),
    );

    for (const point of sorted) {
      seriesMap.set(point.observed_on, point.value);
    }

    for (let index = 0; index < sorted.length; index += 1) {
      const point = sorted[index];
      if (!point) {
        continue;
      }
      const baseline = sorted[index - rollingOffset];
      rollingBaseline.set(point.observed_on, baseline?.value ?? null);
    }

    lookup.set(dataset.dataset_id, seriesMap);
    rollingBaselineLookup.set(dataset.dataset_id, rollingBaseline);
  }

  const fixedBaselineByDataset = new Map<string, SeriesBaseline>();
  if (baselineMode === "fixed") {
    for (const dataset of datasets) {
      fixedBaselineByDataset.set(
        dataset.dataset_id,
        resolveFixedBaseline(dataset.observations, fixedBaselineDate),
      );
    }
  }

  return orderedDates.map((date) => {
    const row: ChartRow = { date };

    for (const dataset of datasets) {
      const series = lookup.get(dataset.dataset_id);
      const rawValue = series?.get(date) ?? null;

      if (valueMode === "observed") {
        row[dataset.dataset_id] = rawValue;
        continue;
      }

      if (rawValue === null) {
        row[dataset.dataset_id] = null;
        continue;
      }

      const baselineValue =
        baselineMode === "rolling"
          ? (rollingBaselineLookup.get(dataset.dataset_id)?.get(date) ?? null)
          : (fixedBaselineByDataset.get(dataset.dataset_id)?.baselineValue ?? null);

      if (baselineValue === null || baselineValue === 0) {
        row[dataset.dataset_id] = null;
        continue;
      }

      row[dataset.dataset_id] = ((rawValue - baselineValue) / baselineValue) * 100;
    }

    return row;
  });
};

const formatDate = (value: string): string => {
  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
    timeZone: "UTC",
  });
};

export const ComparisonPageClient = (): JSX.Element => {
  const [datasetIds, setDatasetIds] = useState<string[]>([]);
  const [datasets, setDatasets] = useState<DatasetDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [stateError, setStateError] = useState<string | null>(null);
  const [chartSettings, setChartSettings] = useState(() => {
    try {
      return getComparisonState().chartSettings;
    } catch {
      return {
        valueMode: "observed" as const,
        baselineMode: "rolling" as const,
        rollingOffset: 1,
        fixedBaselineDate: null,
      };
    }
  });

  useEffect(() => {
    const sync = (): void => {
      try {
        const state = getComparisonState();
        setDatasetIds(state.selectedDatasetIds);
        setChartSettings(state.chartSettings);
        setStateError(null);
      } catch (error) {
        if (error instanceof ComparisonStateCorruptedError) {
          setStateError(error.message);
        }
      }
    };

    sync();
    window.addEventListener(COMPARISON_STATE_EVENT, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener(COMPARISON_STATE_EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  useEffect(() => {
    let isActive = true;

    if (datasetIds.length === 0) {
      setDatasets([]);
      return () => {
        isActive = false;
      };
    }

    setLoading(true);
    void Promise.all(datasetIds.map((datasetId) => fetchDatasetDetail(datasetId)))
      .then((items) => {
        if (isActive) {
          setDatasets(items);
        }
      })
      .catch(() => {
        if (isActive) {
          setDatasets([]);
        }
      })
      .finally(() => {
        if (isActive) {
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [datasetIds]);

  const compatibleForObserved = useMemo(() => {
    const unitTypes = datasets.map((dataset) => dataset.metadata.unit_type ?? null);
    return isComparisonSelectionCompatible(unitTypes);
  }, [datasets]);

  useEffect(() => {
    if (!compatibleForObserved && chartSettings.valueMode === "observed") {
      const next = { ...chartSettings, valueMode: "relative" as const };
      setComparisonChartSettings(next);
      setChartSettings(next);
    }
  }, [chartSettings, compatibleForObserved]);

  const chartRows = useMemo(() => {
    return buildChartRows(
      datasets,
      chartSettings.valueMode,
      chartSettings.baselineMode,
      chartSettings.rollingOffset,
      chartSettings.fixedBaselineDate,
    );
  }, [chartSettings, datasets]);

  const availableBaselineDates = useMemo(() => {
    const dates = new Set<string>();
    for (const dataset of datasets) {
      for (const point of dataset.observations) {
        dates.add(point.observed_on);
      }
    }
    return [...dates].sort((left, right) => parseDate(left) - parseDate(right));
  }, [datasets]);

  const selectedDatasets = useMemo(() => {
    const byId = new Map(datasets.map((dataset) => [dataset.dataset_id, dataset]));
    return datasetIds.map((datasetId) => {
      const dataset = byId.get(datasetId);
      return {
        datasetId,
        title: dataset?.title ?? datasetId,
      };
    });
  }, [datasetIds, datasets]);

  const isAbsoluteMode = chartSettings.valueMode === "observed";

  if (stateError) {
    return (
      <Card
        className="grid gap-3 border border-red-500/50 p-4"
        data-testid="comparison-state-error"
      >
        <p className="text-sm">Comparison state is corrupted and cannot be loaded.</p>
        <Button
          size="sm"
          variant="secondary"
          onPress={() => {
            resetComparisonState();
          }}
        >
          Reset comparison state
        </Button>
      </Card>
    );
  }

  if (datasetIds.length === 0) {
    return (
      <section
        className="rounded-[2rem] border border-(--shell-border) bg-(--shell-surface) p-5"
        data-testid="comparison-empty-state"
      >
        <h2 className="font-semibold text-lg">Comparison</h2>
        <p className="text-default-600 text-sm">
          Select at least two datasets from dataset detail pages to unlock comparison overlays.
        </p>
      </section>
    );
  }

  return (
    <div className="grid gap-4" data-testid="comparison-page-client">
      <Card className="comparison-controls-card grid gap-3 p-4" data-testid="comparison-controls">
        <div
          className="flex flex-wrap items-center gap-2"
          data-testid="comparison-selected-datasets"
        >
          {selectedDatasets.map((dataset) => (
            <Button
              key={dataset.datasetId}
              size="sm"
              variant="secondary"
              className="comparison-control-chip rounded-full transition-colors hover:bg-zinc-300 hover:text-zinc-950 data-[hovered=true]:bg-zinc-300 data-[hovered=true]:text-zinc-950 dark:data-[hovered=true]:bg-zinc-700 dark:data-[hovered=true]:text-white dark:hover:bg-zinc-700 dark:hover:text-white"
              onPress={() => {
                removeComparisonDataset(dataset.datasetId);
              }}
            >
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{
                  backgroundColor: getComparisonLineColor(dataset.datasetId, datasetIds),
                }}
              />
              {dataset.title}
              <span aria-hidden="true">×</span>
            </Button>
          ))}
        </div>

        <div
          className="grid gap-3 sm:grid-cols-[minmax(11rem,12rem)_minmax(11rem,12rem)_minmax(8.5rem,9rem)]"
          data-testid="comparison-mode-controls"
        >
          <Select
            className="comparison-control-select w-full"
            isDisabled={!compatibleForObserved}
            placeholder="Select mode"
            value={chartSettings.valueMode}
            variant="secondary"
            onChange={(value) => {
              const nextMode = value === "relative" ? "relative" : "observed";
              setComparisonChartSettings({ valueMode: nextMode });
            }}
          >
            <Label>Mode</Label>
            <Select.Trigger>
              <Select.Value />
              <Select.Indicator />
            </Select.Trigger>
            <Select.Popover className="comparison-control-popover">
              <ListBox>
                <ListBox.Item
                  className="comparison-control-option"
                  id="observed"
                  textValue="Absolute"
                >
                  Absolute
                  <ListBox.ItemIndicator />
                </ListBox.Item>
                <ListBox.Item
                  className="comparison-control-option"
                  id="relative"
                  textValue="Relative"
                >
                  Relative
                  <ListBox.ItemIndicator />
                </ListBox.Item>
              </ListBox>
            </Select.Popover>
          </Select>

          <Select
            className="comparison-control-select w-full"
            isDisabled={isAbsoluteMode}
            placeholder="Select baseline"
            value={chartSettings.baselineMode}
            variant="secondary"
            onChange={(value) => {
              const nextMode = value === "fixed" ? "fixed" : "rolling";
              setComparisonChartSettings({ baselineMode: nextMode });
            }}
          >
            <Label>Baseline</Label>
            <Select.Trigger>
              <Select.Value />
              <Select.Indicator />
            </Select.Trigger>
            <Select.Popover className="comparison-control-popover">
              <ListBox>
                <ListBox.Item
                  className="comparison-control-option"
                  id="rolling"
                  textValue="Rolling"
                >
                  Rolling
                  <ListBox.ItemIndicator />
                </ListBox.Item>
                <ListBox.Item className="comparison-control-option" id="fixed" textValue="Fixed">
                  Fixed
                  <ListBox.ItemIndicator />
                </ListBox.Item>
              </ListBox>
            </Select.Popover>
          </Select>

          {chartSettings.baselineMode === "rolling" ? (
            <div className="flex w-full flex-col gap-1">
              <Label className="px-1" htmlFor="comparison-rolling-offset">
                Offset
              </Label>
              <Input
                className="comparison-control-input"
                disabled={isAbsoluteMode}
                id="comparison-rolling-offset"
                min={1}
                max={24}
                type="number"
                value={String(chartSettings.rollingOffset)}
                variant="secondary"
                onChange={(event) => {
                  const nextOffset = Number.parseInt(event.target.value, 10);
                  setComparisonChartSettings({
                    rollingOffset: Number.isFinite(nextOffset) ? nextOffset : 1,
                  });
                }}
              />
            </div>
          ) : (
            <Select
              className="comparison-control-select w-full sm:col-span-2"
              isDisabled={isAbsoluteMode}
              placeholder="Select baseline date"
              value={chartSettings.fixedBaselineDate}
              variant="secondary"
              onChange={(value) => {
                setComparisonChartSettings({
                  fixedBaselineDate: value === null ? null : String(value),
                });
              }}
            >
              <Label>Date</Label>
              <Select.Trigger>
                <Select.Value />
                <Select.Indicator />
              </Select.Trigger>
              <Select.Popover className="comparison-control-popover">
                <ListBox>
                  {availableBaselineDates.map((date) => (
                    <ListBox.Item
                      className="comparison-control-option"
                      key={date}
                      id={date}
                      textValue={formatDate(date)}
                    >
                      {formatDate(date)}
                      <ListBox.ItemIndicator />
                    </ListBox.Item>
                  ))}
                </ListBox>
              </Select.Popover>
            </Select>
          )}
        </div>

        {!compatibleForObserved ? (
          <p className="text-amber-700 text-xs" data-testid="comparison-compatibility-message">
            Absolute mode is disabled because selected datasets use different unit types. Relative
            mode is active.
          </p>
        ) : null}
      </Card>

      {datasetIds.length >= 2 ? (
        <Card className="h-135 p-3" data-testid="comparison-chart-card">
          {loading ? (
            <div className="flex h-full items-center justify-center text-default-500 text-sm">
              Loading chart...
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={360}>
              <LineChart data={chartRows} margin={{ top: 16, right: 24, left: 4, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={formatDate} minTickGap={28} />
                <YAxis
                  tickFormatter={(value: number) =>
                    chartSettings.valueMode === "relative"
                      ? `${value.toFixed(1)}%`
                      : value.toFixed(1)
                  }
                />
                <Tooltip labelFormatter={(label) => formatDate(String(label))} />
                <Legend />
                {datasets.map((dataset) => (
                  <Line
                    key={dataset.dataset_id}
                    type="monotone"
                    dataKey={dataset.dataset_id}
                    name={dataset.title}
                    stroke={getComparisonLineColor(dataset.dataset_id, datasetIds)}
                    strokeWidth={2}
                    dot={false}
                    connectNulls={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          )}
        </Card>
      ) : (
        <section
          className="rounded-[2rem] border border-(--shell-border) bg-(--shell-surface) p-4"
          data-testid="comparison-chart-disabled-message"
        >
          <p className="text-default-600 text-sm">
            Select one more dataset to unlock the comparison chart.
          </p>
        </section>
      )}
    </div>
  );
};
