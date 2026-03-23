export interface SourceRef {
  id: string;
  name: string;
}

export interface DatasetSummary {
  dataset_id: string;
  source: SourceRef;
  title: string;
  description: string | null;
  geographic_scope: string | null;
  topic_tags: string[];
  latest_update_at: string;
}

export interface DatasetRecentItem {
  dataset_id: string;
  source: SourceRef;
  title: string;
  latest_update_at: string;
}

export interface DatasetSourceGroup {
  source: SourceRef;
  dataset_count: number;
  dataset_ids: string[];
}

export interface ObservationPoint {
  observed_on: string;
  value: number;
  reported_at: string;
  attributes: Record<string, unknown>;
}

export interface DatasetDetail {
  dataset_id: string;
  source: SourceRef;
  title: string;
  description: string | null;
  geographic_scope: string | null;
  topic_tags: string[];
  metadata: Record<string, string | null>;
  observations: ObservationPoint[];
  observation_sort: string;
}

export interface DatasetSearchResponse {
  items: DatasetSummary[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  sort: string;
}

export interface DatasetRecentUpdatesResponse {
  items: DatasetRecentItem[];
  limit: number;
  sort: string;
}

export interface DatasetCatalogResponse {
  items: DatasetSummary[];
  groups: DatasetSourceGroup[] | null;
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  sort: string;
}

export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
  };
}

export type CatalogViewMode = "flat" | "grouped";

export interface ChartDataPoint {
  date: string;
  value: number;
}

export const DISCOVERY_TYPES_SCHEMA_VERSION = "v1";
