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
    datasets: [firstDataset],
    sort: "title_asc,dataset_id_asc",
  };
};

export const buildGeographyDetailFixture = (): GeographyDetail => ({
  geography: {
    id: "us",
    label: "US",
    dataset_count: 2,
  },
  datasets: buildSourceDatasetsFixture(),
  sort: "title_asc,dataset_id_asc",
});
