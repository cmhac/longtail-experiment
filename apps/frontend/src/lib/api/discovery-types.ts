export interface SourceRef {
  id: string;
  name: string;
}

export interface SourceSummary {
  id: string;
  title: string;
  description: string;
  dataset_count: number;
  source_type?: string | null;
}

export interface DatasetSummary {
  dataset_id: string;
  source: SourceRef;
  title: string;
  description: string | null;
  category?: string | null;
  geographic_scope: string | null;
  topic_tags: string[];
  latest_update_at: string;
}

export interface PaginatedCollectionMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface PaginatedDatasetCollection extends PaginatedCollectionMeta {
  items: DatasetSummary[];
  sort: string;
}

export interface DatasetRecentItem {
  dataset_id: string;
  source: SourceRef;
  title: string;
  description?: string | null;
  geographic_scope?: string | null;
  topic_tags: string[];
  latest_update_at: string;
  action_links: {
    view_table_href: string;
    download_csv_href: string;
  };
}

export interface DatasetSourceGroup {
  source: SourceRef;
  dataset_count: number;
  dataset_ids: string[];
}

export interface DatasetCatalogSourceAggregation {
  source: SourceRef;
  dataset_count: number;
}

export interface DatasetCatalogCategoryAggregation {
  value: string;
  dataset_count: number;
}

export interface DatasetCatalogAggregations {
  total_dataset_count: number;
  sources: DatasetCatalogSourceAggregation[];
  categories: DatasetCatalogCategoryAggregation[];
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

export interface SearchScopeSummaryResponse {
  active_dataset_count: number;
  active_source_count: number;
  generated_at?: string;
}

export interface SuggestionItem {
  dataset_id: string;
  source: SourceRef;
  title: string;
  rank_score: number;
}

export interface DatasetSearchSuggestionsResponse {
  query: string;
  limit: number;
  items: SuggestionItem[];
}

export interface DatasetRecentUpdatesResponse {
  items: DatasetRecentItem[];
  limit: number;
  sort: string;
}

export interface DatasetCatalogResponse {
  items: DatasetSummary[];
  groups: DatasetSourceGroup[] | null;
  aggregations: DatasetCatalogAggregations;
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  sort: string;
}

export interface SourceListResponse {
  items: SourceSummary[];
  total_items: number;
  sort: string;
}

export interface SourceDetail {
  source: SourceSummary;
  items: DatasetSummary[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  sort: string;
}

export interface TopicSummary {
  id: string;
  label: string;
  dataset_count: number;
}

export interface TopicDetail {
  topic: TopicSummary;
  items: DatasetSummary[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  sort: string;
}

export interface GeographySummary {
  id: string;
  label: string;
  dataset_count: number;
}

export interface GeographyDetail {
  geography: GeographySummary;
  items: DatasetSummary[];
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
