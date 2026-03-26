import type { DatasetDetail } from "../../src/lib/api/discovery-types";

export const buildDatasetDetailFixture = (): DatasetDetail => {
  return {
    dataset_id: "GAS.REG.CO",
    source: { id: "eia", name: "EIA" },
    title: "Regular All Formulations Retail Gasoline Prices - Colorado",
    description: "Retail gasoline prices for Colorado.",
    geographic_scope: "Colorado",
    topic_tags: ["energy", "gasoline"],
    metadata: {
      unit: "$/Gal",
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
    observation_sort: "observed_on_asc,reported_at_asc",
  };
};
