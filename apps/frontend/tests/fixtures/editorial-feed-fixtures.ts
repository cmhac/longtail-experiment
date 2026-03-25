import type { DatasetRecentItem } from "../../src/lib/api/discovery-types";

export const makeEditorialFeedItem = (index: number): DatasetRecentItem => {
  const datasetId = `DATASET_${index}`;

  return {
    dataset_id: datasetId,
    source: { id: "eia", name: "EIA" },
    title: `Editorial Dataset ${index}`,
    description: `Weekly update summary for editorial dataset ${index}.`,
    geographic_scope: "US",
    topic_tags: ["energy", "retail fuel prices"],
    latest_update_at: `2026-03-${String(25 - index).padStart(2, "0")}T00:00:00Z`,
    action_links: {
      view_table_href: `/datasets/${datasetId}`,
      download_csv_href: `/api/datasets/${datasetId}.csv`,
    },
  };
};

export const makeEditorialFeedItems = (count: number): DatasetRecentItem[] => {
  return Array.from({ length: count }, (_, index) => makeEditorialFeedItem(index + 1));
};
