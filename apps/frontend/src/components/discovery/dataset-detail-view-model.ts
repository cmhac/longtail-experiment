import type { DatasetDetail, ObservationPoint } from "../../lib/api/discovery-types";

export type TrendRangeKey = "1M" | "6M" | "1Y" | "ALL";

export type MovementState = "positive" | "negative" | "neutral" | "unavailable";
type UnitType = "usd" | "percent" | "number";

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

const SUPPORTED_UNIT_TYPES: UnitType[] = ["usd", "percent", "number"];

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

const normalizeUnitType = (value: unknown): UnitType | null => {
  if (typeof value !== "string") {
    return null;
  }
  const normalized = value.trim().toLowerCase();
  if (SUPPORTED_UNIT_TYPES.includes(normalized as UnitType)) {
    return normalized as UnitType;
  }
  return null;
};

const inferUnitTypeFromLabel = (value: string | null): UnitType | null => {
  if (!value) {
    return null;
  }
  const normalized = value.trim().toLowerCase();
  if (normalized === "") {
    return null;
  }
  if (normalized.includes("%") || normalized.includes("percent")) {
    return "percent";
  }
  if (normalized.includes("$") || normalized.includes("dollar")) {
    return "usd";
  }
  return "number";
};

export const formatValue = (
  value: number,
  unitType?: string | null,
  unitLabel?: string | null,
): string => {
  const resolvedUnitType = normalizeUnitType(unitType) ?? inferUnitTypeFromLabel(unitLabel ?? null);
  if (resolvedUnitType === "percent") {
    return `${formatNumber(value, 3)}%`;
  }
  if (resolvedUnitType === "number") {
    return formatNumber(value, 3);
  }

  const formatted = `$${formatNumber(value, 3)}`;
  if (!unitLabel) {
    return formatted;
  }
  return `${formatted}${unitLabel.startsWith("/") ? "" : " "}${unitLabel}`;
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

const getUnitType = (detail: DatasetDetail): UnitType | null => {
  const value = detail.metadata.unit_type;
  return normalizeUnitType(typeof value === "string" ? value : null);
};

const getDerivedFrequencyLabel = (observations: ObservationPoint[]): string => {
  const observedOnDates = [...new Set(observations.map((item) => item.observed_on))]
    .map((value) => Date.parse(`${value}T00:00:00Z`))
    .filter((value) => Number.isFinite(value))
    .sort((a, b) => a - b)
    .slice(-5);

  if (observedOnDates.length < 2) {
    return "--";
  }

  const deltasInDays: number[] = [];
  for (let index = 1; index < observedOnDates.length; index += 1) {
    const previous = observedOnDates[index - 1];
    const current = observedOnDates[index];
    if (previous === undefined || current === undefined) {
      continue;
    }
    deltasInDays.push(Math.round((current - previous) / 86_400_000));
  }

  if (deltasInDays.length === 0) {
    return "--";
  }

  const averageDelta = deltasInDays.reduce((sum, value) => sum + value, 0) / deltasInDays.length;

  if (averageDelta <= 2) {
    return "Daily";
  }
  if (averageDelta <= 10) {
    return "Weekly";
  }
  if (averageDelta <= 45) {
    return "Monthly";
  }
  if (averageDelta <= 100) {
    return "Quarterly";
  }
  return "Yearly";
};

export const buildInsightMetrics = (detail: DatasetDetail): InsightMetric[] => {
  const observations = detail.observations;

  if (observations.length === 0) {
    return [
      { label: "Latest Observation", value: "No data available" },
      { label: "1-Year High", value: "--" },
      { label: "1-Year Low", value: "--" },
    ];
  }

  const unit = getUnit(detail);
  const unitType = getUnitType(detail);
  const latest = observations[observations.length - 1];
  if (!latest) {
    return [
      { label: "Latest Observation", value: "No data available" },
      { label: "1-Year High", value: "--" },
      { label: "1-Year Low", value: "--" },
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
    value: formatValue(latest.value, unitType, unit),
    ...(latestMovementSummary ? { movementSummary: latestMovementSummary } : {}),
    ...(movementState && movementState !== "unavailable" ? { movementState } : {}),
  };

  return [
    latestMetric,
    { label: "1-Year High", value: formatValue(high, unitType, unit) },
    { label: "1-Year Low", value: formatValue(low, unitType, unit) },
  ];
};

export const buildObservationRows = (
  observations: ObservationPoint[],
  unitType?: string | null,
  unitLabel?: string | null,
): ObservationRowViewModel[] => {
  const reversed = [...observations].reverse();

  return reversed.map((observation, index) => {
    const previous = reversed[index + 1] ?? null;
    const weeklyChange = previous ? observation.value - previous.value : null;

    return {
      observedOn: formatObservedOn(observation.observed_on),
      valueDisplay: formatValue(observation.value, unitType, unitLabel),
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
    { key: "Frequency", value: getDerivedFrequencyLabel(detail.observations) },
    { key: "Source Type", value: detail.metadata.source_type ?? null },
  ];

  return candidates.map((item) => ({ key: item.key, value: item.value ?? "--" }));
};
