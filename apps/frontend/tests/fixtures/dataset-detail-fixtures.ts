import type { DatasetDetail, ObservationPoint } from "../../src/lib/api/discovery-types";

interface ObservationHistoryOptions {
  count: number;
  dayStep?: number;
  initialValue?: number;
  start: string;
  valueStep?: number;
}

export const buildObservationHistory = ({
  count,
  dayStep = 7,
  initialValue = 1,
  start,
  valueStep = 1,
}: ObservationHistoryOptions): ObservationPoint[] => {
  const startDate = new Date(`${start}T00:00:00Z`);

  return Array.from({ length: count }, (_, index) => {
    const observedAt = new Date(startDate);
    observedAt.setUTCDate(startDate.getUTCDate() + index * dayStep);
    const observedOn = observedAt.toISOString().slice(0, 10);

    return {
      observed_on: observedOn,
      value: initialValue + index * valueStep,
      reported_at: `${observedOn}T00:00:00Z`,
      attributes: {},
    };
  });
};

export const buildDatasetDetailFixture = (
  overrides: Partial<DatasetDetail> = {},
): DatasetDetail => {
  const base: DatasetDetail = {
    dataset_id: "GAS.REG.CO",
    source: { id: "eia", name: "EIA" },
    title: "Regular All Formulations Retail Gasoline Prices - Colorado",
    description: "Retail gasoline prices for Colorado.",
    geographic_scope: "Colorado",
    topic_tags: ["energy", "gasoline"],
    metadata: {
      unit: "$/Gal",
      unit_type: "usd",
      source_type: "Federal",
    },
    observations: [
      {
        observed_on: "2024-01-01",
        value: 3.175,
        reported_at: "2024-01-02T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-01-08",
        value: 3.139,
        reported_at: "2024-01-09T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-01-15",
        value: 3.15,
        reported_at: "2024-01-16T00:00:00Z",
        attributes: {},
      },
    ],
    has_recent_notification: true,
    canonical_trend_descriptor: {
      descriptor_state: "available",
      trend_label: "moderate_uptrend",
      direction: "up",
      strength: "moderate",
      selected_lookback_points: 10,
      observed_on: "2024-01-15",
      reason_code: null,
    },
    lookback_trend_snapshots: [
      {
        lookback_points: 10,
        applicability_state: "applicable",
        outcome_state: "significant_trend",
        trend_label: "moderate_uptrend",
        direction: "up",
        strength: "moderate",
        reason_code: null,
      },
    ],
    observation_sort: "observed_on_asc,reported_at_asc",
  };

  return {
    ...base,
    ...overrides,
    metadata: {
      ...base.metadata,
      ...(overrides.metadata ?? {}),
    },
    observations: overrides.observations ?? base.observations,
    source: overrides.source ?? base.source,
    topic_tags: overrides.topic_tags ?? base.topic_tags,
  };
};

export const buildLongHistoryDatasetDetailFixture = (): DatasetDetail => {
  return buildDatasetDetailFixture({
    observations: buildObservationHistory({
      count: 340,
      initialValue: 2.5,
      start: "2018-01-01",
      valueStep: 0.02,
    }),
  });
};

export const buildLimitedHistoryDatasetDetailFixture = (): DatasetDetail => {
  return buildDatasetDetailFixture({
    observations: buildObservationHistory({
      count: 8,
      initialValue: 3,
      start: "2024-01-01",
      valueStep: 0.05,
    }),
  });
};

export const buildNoObservationsDatasetDetailFixture = (): DatasetDetail => {
  return buildDatasetDetailFixture({ observations: [] });
};

export const buildRelativeChangeFixture = (): DatasetDetail => {
  return buildDatasetDetailFixture({
    observations: [
      {
        observed_on: "2024-01-01",
        value: 100,
        reported_at: "2024-01-01T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-01-08",
        value: 110,
        reported_at: "2024-01-08T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-01-15",
        value: 121,
        reported_at: "2024-01-15T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-01-22",
        value: 100,
        reported_at: "2024-01-22T00:00:00Z",
        attributes: {},
      },
    ],
  });
};

export const buildZeroBaselineFixture = (): DatasetDetail => {
  return buildDatasetDetailFixture({
    observations: [
      {
        observed_on: "2024-01-01",
        value: 0,
        reported_at: "2024-01-01T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-01-08",
        value: 10,
        reported_at: "2024-01-08T00:00:00Z",
        attributes: {},
      },
    ],
  });
};
