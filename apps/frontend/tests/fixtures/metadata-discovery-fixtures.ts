import type { GeographyDetail, TopicDetail } from "../../src/lib/api/discovery-types";
import { buildSourceDatasetsFixture } from "./source-discovery-fixtures";

export const buildTopicDetailFixture = (): TopicDetail => {
  const [firstDataset] = buildSourceDatasetsFixture();
  if (!firstDataset) {
    throw new Error("Expected source dataset fixture to include at least one dataset");
  }

  return {
    topic: {
      id: "inflation",
      label: "inflation",
      dataset_count: 1,
    },
    items: [firstDataset],
    page: 1,
    page_size: 20,
    total_items: 1,
    total_pages: 1,
    sort: "title_asc,dataset_id_asc",
  };
};

export const buildGeographyDetailFixture = (): GeographyDetail => ({
  geography: {
    id: "us",
    label: "US",
    dataset_count: 2,
  },
  items: buildSourceDatasetsFixture(),
  page: 1,
  page_size: 20,
  total_items: 2,
  total_pages: 1,
  sort: "title_asc,dataset_id_asc",
});
