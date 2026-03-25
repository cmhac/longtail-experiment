import type { DatasetDetail, ObservationPoint } from "../../lib/api/discovery-types";

export type TrendRangeKey = "1M" | "6M" | "1Y" | "ALL";

export type MovementState = "positive" | "negative" | "neutral" | "unavailable";

export interface InsightMetric {
  label: string;
  value: string;
  movementSummary?: string;
  movementState?: Exclude<MovementState, "unavailable">;
}

export interface ObservationRowViewModel {
  observedOn: string;
  valueDisplay: string;
  weeklyChangeDisplay: string;
  movementState: MovementState;
}

const RANGES_TO_COUNTS: Record<Exclude<TrendRangeKey, "ALL">, number> = {
  "1M": 4,
  "6M": 26,
  "1Y": 52,
};

const formatNumber = (value: number, maximumFractionDigits: number): string => {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits,
    minimumFractionDigits: maximumFractionDigits,
  }).format(value);
};

const formatSigned = (value: number, maximumFractionDigits: number): string => {
  const abs = Math.abs(value);
  const sign = value > 0 ? "+" : value < 0 ? "-" : "";
  return `${sign}${formatNumber(abs, maximumFractionDigits)}`;
};

export const formatObservedOn = (value: string): string => {
  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleDateString("en-US", {
    day: "2-digit",
    month: "short",
    timeZone: "UTC",
    year: "numeric",
  });
};

export const formatValue = (value: number, unit?: string | null): string => {
  const formatted = `$${formatNumber(value, 3)}`;

  if (!unit) {
    return formatted;
  }

  return `${formatted}${unit.startsWith("/") ? "" : " "}${unit}`;
};

const toMovementState = (value: number | null): MovementState => {
  if (value === null) {
    return "unavailable";
  }

  if (value > 0) {
    return "positive";
  }

  if (value < 0) {
    return "negative";
  }

  return "neutral";
};

const getUnit = (detail: DatasetDetail): string | null => {
  const value = detail.metadata.unit ?? detail.metadata.units;
  return typeof value === "string" ? value : null;
};

export const buildInsightMetrics = (detail: DatasetDetail): InsightMetric[] => {
  const observations = detail.observations;

  if (observations.length === 0) {
    return [
      { label: "Latest Observation", value: "No data available" },
      { label: "52 Week High", value: "--" },
      { label: "52 Week Low", value: "--" },
    ];
  }

  const unit = getUnit(detail);
  const latest = observations[observations.length - 1];
  if (!latest) {
    return [
      { label: "Latest Observation", value: "No data available" },
      { label: "52 Week High", value: "--" },
      { label: "52 Week Low", value: "--" },
    ];
  }
  const previous = observations.length > 1 ? observations[observations.length - 2] : null;
  const latestMovement = previous ? latest.value - previous.value : null;
  const latestMovementSummary =
    latestMovement === null
      ? undefined
      : `${formatSigned(latestMovement, 3)} vs previous observation`;
  const movementState = latestMovement === null ? undefined : toMovementState(latestMovement);

  const lookbackWindow = observations.slice(-52);
  const values = lookbackWindow.map((item) => item.value);
  const high = Math.max(...values);
  const low = Math.min(...values);

  const latestMetric: InsightMetric = {
    label: "Latest Observation",
    value: formatValue(latest.value, unit),
    ...(latestMovementSummary ? { movementSummary: latestMovementSummary } : {}),
    ...(movementState && movementState !== "unavailable" ? { movementState } : {}),
  };

  return [
    latestMetric,
    { label: "52 Week High", value: formatValue(high, unit) },
    { label: "52 Week Low", value: formatValue(low, unit) },
  ];
};

export const buildObservationRows = (
  observations: ObservationPoint[],
  unit?: string | null,
): ObservationRowViewModel[] => {
  const reversed = [...observations].reverse();

  return reversed.map((observation, index) => {
    const previous = reversed[index + 1] ?? null;
    const weeklyChange = previous ? observation.value - previous.value : null;

    return {
      observedOn: formatObservedOn(observation.observed_on),
      valueDisplay: formatValue(observation.value, unit),
      weeklyChangeDisplay: weeklyChange === null ? "--" : formatSigned(weeklyChange, 3),
      movementState: toMovementState(weeklyChange),
    };
  });
};

export const filterObservationRange = (
  observations: ObservationPoint[],
  range: TrendRangeKey,
): ObservationPoint[] => {
  if (range === "ALL") {
    return observations;
  }

  const count = RANGES_TO_COUNTS[range];
  if (observations.length <= count) {
    return observations;
  }

  return observations.slice(-count);
};

export const getMetadataRows = (detail: DatasetDetail): Array<{ key: string; value: string }> => {
  const candidates: Array<{ key: string; value: string | null }> = [
    { key: "Frequency", value: detail.metadata.frequency_granularity ?? null },
    { key: "Source Type", value: detail.metadata.source_type ?? null },
  ];

  return candidates.map((item) => ({ key: item.key, value: item.value ?? "--" }));
};
