import type { CanonicalTrendDescriptor, LookbackTrendEvidence } from "./discovery-types";

export type DatasetDetailTrendDescriptor = CanonicalTrendDescriptor;
export type DatasetDetailLookbackSnapshot = LookbackTrendEvidence;

export interface TrendFeedItem {
  item_type: "trend_event";
  dataset_id: string;
  source: { id: string; name: string };
  title: string;
  direction: "up" | "down";
  confidence_score: number | null;
  start_period: string;
  latest_update_at: string;
  action_links: {
    view_table_href: string;
    download_csv_href: string;
  };
}
