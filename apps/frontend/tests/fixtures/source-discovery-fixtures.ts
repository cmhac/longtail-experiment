import type {
  DatasetSummary,
  SourceDetail,
  SourceListResponse,
} from "../../src/lib/api/discovery-types";

export const buildSourceListFixture = (): SourceListResponse => ({
  items: [
    {
      id: "bea",
      name: "BEA",
      dataset_count: 1,
      source_type: "external",
    },
    {
      id: "fred",
      name: "FRED",
      dataset_count: 2,
      source_type: "external",
    },
  ],
  total_items: 2,
  sort: "source_name_asc,source_id_asc",
});

export const buildSourceDatasetsFixture = (): DatasetSummary[] => [
  {
    dataset_id: "CPIAUCSL",
    source: { id: "fred", name: "FRED" },
    title: "Consumer Price Index",
    description: "All Urban Consumers",
    geographic_scope: "US",
    topic_tags: ["inflation", "prices"],
    latest_update_at: "2026-02-15T00:00:00Z",
  },
  {
    dataset_id: "UNRATE",
    source: { id: "fred", name: "FRED" },
    title: "Unemployment Rate",
    description: "Percent of labor force unemployed",
    geographic_scope: "US",
    topic_tags: ["labor", "employment"],
    latest_update_at: "2026-02-10T00:00:00Z",
  },
];

export const buildSourceDetailFixture = (): SourceDetail => ({
  source: {
    id: "fred",
    name: "FRED",
    dataset_count: 2,
    source_type: "external",
  },
  items: buildSourceDatasetsFixture(),
  page: 1,
  page_size: 20,
  total_items: 2,
  total_pages: 1,
  sort: "title_asc,dataset_id_asc",
});
