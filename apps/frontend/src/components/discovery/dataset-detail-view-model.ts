import type {
  ChartValueMode,
  DatasetDetail,
  ObservationPoint,
  RelativeBaselineMode,
  RelativeComputabilityState,
} from "../../lib/api/discovery-types";

export type TrendRangeKey = "1M" | "6M" | "1Y" | "5Y" | "ALL";

export type MovementState = "positive" | "negative" | "neutral" | "unavailable";
type UnitType = "usd" | "percent" | "number";

export interface RelativeChangeSettings {
  baselineMode: RelativeBaselineMode;
  fixedBaselineDate: string | null;
  rollingOffset: number;
  valueMode: ChartValueMode;
}

export interface RelativeChangePoint {
  baselineObservedOn: string | null;
  computability: RelativeComputabilityState;
  observed_on: string;
  value: number | null;
}

export interface RelativeChangeProjection {
  availableDates: string[];
  hasComputablePoints: boolean;
  points: RelativeChangePoint[];
  selectedFixedBaselineDate: string | null;
}

export const DEFAULT_RELATIVE_CHANGE_SETTINGS: RelativeChangeSettings = {
  baselineMode: "rolling",
  fixedBaselineDate: null,
  rollingOffset: 1,
  valueMode: "observed",
};

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

const RANGE_LABEL_PREFIX: Record<TrendRangeKey, string> = {
  "1M": "1-Month",
  "6M": "6-Month",
  "1Y": "1-Year",
  "5Y": "5-Year",
  ALL: "All-Time",
};

const SUPPORTED_UNIT_TYPES: UnitType[] = ["usd", "percent", "number"];

const TREND_RANGE_ORDER: TrendRangeKey[] = ["ALL", "5Y", "1Y", "6M", "1M"];

const RANGE_TO_DAYS: Record<Exclude<TrendRangeKey, "ALL">, number> = {
  "1M": 30,
  "6M": 183,
  "1Y": 365,
  "5Y": 365 * 5,
};

const DAY_IN_MILLISECONDS = 86_400_000;

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

const toChronologicalObservations = (observations: ObservationPoint[]): ObservationPoint[] => {
  return [...observations].sort((left, right) => {
    const leftObserved = Date.parse(`${left.observed_on}T00:00:00Z`);
    const rightObserved = Date.parse(`${right.observed_on}T00:00:00Z`);

    if (
      Number.isFinite(leftObserved) &&
      Number.isFinite(rightObserved) &&
      leftObserved !== rightObserved
    ) {
      return leftObserved - rightObserved;
    }

    const leftReported = Date.parse(left.reported_at);
    const rightReported = Date.parse(right.reported_at);
    if (
      Number.isFinite(leftReported) &&
      Number.isFinite(rightReported) &&
      leftReported !== rightReported
    ) {
      return leftReported - rightReported;
    }

    return 0;
  });
};

export const toRollingBaselineIndex = (currentIndex: number, rollingOffset: number): number => {
  return currentIndex - rollingOffset;
};

export const computeRelativeChangePercent = (
  currentValue: number,
  baselineValue: number,
): number | null => {
  if (baselineValue === 0) {
    return null;
  }
  return ((currentValue - baselineValue) / baselineValue) * 100;
};

const buildRollingRelativePoint = (
  observations: ObservationPoint[],
  index: number,
  rollingOffset: number,
): RelativeChangePoint => {
  const observation = observations[index];
  if (!observation) {
    return {
      baselineObservedOn: null,
      computability: "missing-baseline",
      observed_on: "",
      value: null,
    };
  }

  const baselineIndex = toRollingBaselineIndex(index, rollingOffset);
  if (baselineIndex < 0) {
    return {
      baselineObservedOn: null,
      computability: "insufficient-history",
      observed_on: observation.observed_on,
      value: null,
    };
  }

  const baseline = observations[baselineIndex];
  if (!baseline) {
    return {
      baselineObservedOn: null,
      computability: "missing-baseline",
      observed_on: observation.observed_on,
      value: null,
    };
  }

  const value = computeRelativeChangePercent(observation.value, baseline.value);
  return {
    baselineObservedOn: baseline.observed_on,
    computability: value === null ? "zero-baseline" : "computable",
    observed_on: observation.observed_on,
    value,
  };
};

const resolveFixedBaselineIndex = (
  observations: ObservationPoint[],
  settings: RelativeChangeSettings,
): number | null => {
  if (!settings.fixedBaselineDate) {
    return null;
  }

  const index = observations.findIndex(
    (observation) => observation.observed_on === settings.fixedBaselineDate,
  );
  return index >= 0 ? index : null;
};

const buildFixedRelativePoint = (
  observations: ObservationPoint[],
  index: number,
  baselineIndex: number | null,
): RelativeChangePoint => {
  const observation = observations[index];
  if (!observation) {
    return {
      baselineObservedOn: null,
      computability: "missing-baseline",
      observed_on: "",
      value: null,
    };
  }

  if (baselineIndex === null) {
    return {
      baselineObservedOn: null,
      computability: "missing-baseline",
      observed_on: observation.observed_on,
      value: null,
    };
  }

  const baseline = observations[baselineIndex];
  if (!baseline) {
    return {
      baselineObservedOn: null,
      computability: "missing-baseline",
      observed_on: observation.observed_on,
      value: null,
    };
  }

  if (index < baselineIndex) {
    return {
      baselineObservedOn: baseline.observed_on,
      computability: "before-fixed-baseline",
      observed_on: observation.observed_on,
      value: null,
    };
  }

  const value = computeRelativeChangePercent(observation.value, baseline.value);
  return {
    baselineObservedOn: baseline.observed_on,
    computability: value === null ? "zero-baseline" : "computable",
    observed_on: observation.observed_on,
    value,
  };
};

export const projectRelativeChangeSeries = (
  observations: ObservationPoint[],
  settings: RelativeChangeSettings,
): RelativeChangeProjection => {
  const chronological = toChronologicalObservations(observations);
  const availableDates = chronological.map((observation) => observation.observed_on);
  const fixedBaselineIndex = resolveFixedBaselineIndex(chronological, settings);

  const selectedFixedBaselineDate = settings.fixedBaselineDate;

  const points = chronological.map((_, index) => {
    if (settings.baselineMode === "rolling") {
      const rollingOffset = Math.max(1, Math.floor(settings.rollingOffset));
      return buildRollingRelativePoint(chronological, index, rollingOffset);
    }

    return buildFixedRelativePoint(chronological, index, fixedBaselineIndex);
  });

  return {
    availableDates,
    hasComputablePoints: points.some((point) => point.computability === "computable"),
    points,
    selectedFixedBaselineDate,
  };
};

export const projectRelativeChangeGaps = (
  points: RelativeChangePoint[],
): Array<{ date: string; value: number | null }> => {
  return points.map((point) => ({ date: point.observed_on, value: point.value }));
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

export const buildInsightMetrics = (
  detail: DatasetDetail,
  selectedRange: TrendRangeKey = "ALL",
  settings: RelativeChangeSettings = DEFAULT_RELATIVE_CHANGE_SETTINGS,
): InsightMetric[] => {
  const observations = filterObservationRange(detail.observations, selectedRange);
  const windowLabelPrefix = RANGE_LABEL_PREFIX[selectedRange];

  if (observations.length === 0) {
    return [
      { label: "Latest Observation", value: "No data available" },
      { label: `${windowLabelPrefix} High`, value: "--" },
      { label: `${windowLabelPrefix} Low`, value: "--" },
    ];
  }

  const unit = getUnit(detail);
  const unitType = getUnitType(detail);
  if (settings.valueMode === "relative") {
    const projection = projectRelativeChangeSeries(observations, settings);
    const computable = projection.points.filter(
      (point): point is RelativeChangePoint & { value: number } =>
        point.computability === "computable" && point.value !== null,
    );

    if (computable.length === 0) {
      return [
        { label: "Latest Observation", value: "No computable relative points" },
        { label: `${windowLabelPrefix} High`, value: "--" },
        { label: `${windowLabelPrefix} Low`, value: "--" },
      ];
    }

    const latestComputable = computable[computable.length - 1];
    if (!latestComputable) {
      return [
        { label: "Latest Observation", value: "No computable relative points" },
        { label: `${windowLabelPrefix} High`, value: "--" },
        { label: `${windowLabelPrefix} Low`, value: "--" },
      ];
    }
    const previousComputable = computable.length > 1 ? computable[computable.length - 2] : null;
    const latestMovement =
      previousComputable?.value !== undefined
        ? latestComputable.value - previousComputable.value
        : null;
    const relativeMovementState =
      latestMovement === null
        ? undefined
        : latestMovement > 0
          ? "positive"
          : latestMovement < 0
            ? "negative"
            : "neutral";

    const high = Math.max(...computable.map((point) => point.value));
    const low = Math.min(...computable.map((point) => point.value));

    return [
      {
        label: "Latest Observation",
        value: formatValue(latestComputable.value, "percent"),
        ...(latestMovement === null
          ? {}
          : {
              movementSummary: `${formatSigned(latestMovement, 3)} vs previous relative point`,
              ...(relativeMovementState ? { movementState: relativeMovementState } : {}),
            }),
      },
      { label: `${windowLabelPrefix} High`, value: formatValue(high, "percent") },
      { label: `${windowLabelPrefix} Low`, value: formatValue(low, "percent") },
    ];
  }

  const latest = observations[observations.length - 1];
  if (!latest) {
    return [
      { label: "Latest Observation", value: "No data available" },
      { label: `${windowLabelPrefix} High`, value: "--" },
      { label: `${windowLabelPrefix} Low`, value: "--" },
    ];
  }
  const previous = observations.length > 1 ? observations[observations.length - 2] : null;
  const latestMovement = previous ? latest.value - previous.value : null;
  const latestMovementSummary =
    latestMovement === null
      ? undefined
      : `${formatSigned(latestMovement, 3)} vs previous observation`;
  const movementState = latestMovement === null ? undefined : toMovementState(latestMovement);

  const lookbackWindow = filterObservationRange(observations, selectedRange);
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
    { label: `${windowLabelPrefix} High`, value: formatValue(high, unitType, unit) },
    { label: `${windowLabelPrefix} Low`, value: formatValue(low, unitType, unit) },
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

  const latestObservation = observations[observations.length - 1];
  if (!latestObservation) {
    return observations;
  }

  const latestTimestamp = Date.parse(`${latestObservation.observed_on}T00:00:00Z`);
  if (!Number.isFinite(latestTimestamp)) {
    return observations;
  }

  const cutoffTimestamp = latestTimestamp - RANGE_TO_DAYS[range] * DAY_IN_MILLISECONDS;
  return observations.filter((observation) => {
    const observedTimestamp = Date.parse(`${observation.observed_on}T00:00:00Z`);
    return Number.isFinite(observedTimestamp) && observedTimestamp >= cutoffTimestamp;
  });
};

export const getAvailableTrendRanges = (observations: ObservationPoint[]): TrendRangeKey[] => {
  if (observations.length === 0) {
    return [];
  }

  const firstObservation = observations[0];
  const lastObservation = observations[observations.length - 1];
  if (!firstObservation || !lastObservation) {
    return ["ALL"];
  }

  const firstTimestamp = Date.parse(`${firstObservation.observed_on}T00:00:00Z`);
  const lastTimestamp = Date.parse(`${lastObservation.observed_on}T00:00:00Z`);
  if (!Number.isFinite(firstTimestamp) || !Number.isFinite(lastTimestamp)) {
    return ["ALL"];
  }

  const historySpanInDays = (lastTimestamp - firstTimestamp) / DAY_IN_MILLISECONDS;

  return TREND_RANGE_ORDER.filter((range) => {
    if (range === "ALL") {
      return true;
    }

    return historySpanInDays >= RANGE_TO_DAYS[range];
  });
};

export const getMetadataRows = (detail: DatasetDetail): Array<{ key: string; value: string }> => {
  const candidates: Array<{ key: string; value: string | null }> = [
    { key: "Frequency", value: getDerivedFrequencyLabel(detail.observations) },
    { key: "Source Type", value: detail.metadata.source_type ?? null },
  ];

  return candidates.map((item) => ({ key: item.key, value: item.value ?? "--" }));
};
