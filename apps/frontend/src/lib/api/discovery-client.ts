import type {
  ApiErrorEnvelope,
  CanonicalTrendDescriptor,
  DatasetAsOfTrendResponse,
  DatasetCatalogResponse,
  DatasetDetail,
  DatasetRecentUpdatesResponse,
  DatasetSearchResponse,
  DatasetSearchSuggestionsResponse,
  GeographyDetail,
  SearchScopeSummaryResponse,
  SourceDetail,
  SourceListResponse,
  TopicDetail,
} from "./discovery-types";

// Discovery pagination rollout checklist: list endpoints should serialize
// page/page_size consistently through this shared helper.

export class DiscoveryApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(message: string, status: number, code = "unknown_error") {
    super(message);
    this.name = "DiscoveryApiError";
    this.status = status;
    this.code = code;
  }
}

const getApiBaseUrl = (): string => {
  const value = process.env.DISCOVERY_API_BASE_URL;

  if (!value) {
    throw new Error("Missing DISCOVERY_API_BASE_URL");
  }

  return value.replace(/\/$/, "");
};

const createUrl = (path: string, params?: Record<string, string>): string => {
  const baseUrl = getApiBaseUrl();
  const url = new URL(`${baseUrl}${path}`);

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      url.searchParams.set(key, value);
    }
  }

  return url.toString();
};

const parseResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    let code = "http_error";
    let message = `Request failed with status ${response.status}`;

    try {
      const payload = (await response.json()) as ApiErrorEnvelope;
      code = payload.error?.code ?? code;
      message = payload.error?.message ?? message;
    } catch {
      // Keep fallback message when payload is not JSON.
    }

    throw new DiscoveryApiError(message, response.status, code);
  }

  return (await response.json()) as T;
};

const appendPaginationQueryParams = (
  query: Record<string, string>,
  params: { page?: number; pageSize?: number },
): void => {
  if (params.page !== undefined) {
    query.page = String(params.page);
  }

  if (params.pageSize !== undefined) {
    query.page_size = String(params.pageSize);
  }
};

const VALID_LOOKBACK_POINTS = [1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500, 1000] as const;

const isLookbackPoints = (
  value: unknown,
): value is CanonicalTrendDescriptor["selected_lookback_points"] => {
  return (
    typeof value === "number" &&
    VALID_LOOKBACK_POINTS.includes(value as (typeof VALID_LOOKBACK_POINTS)[number])
  );
};

const defaultCanonicalTrendDescriptor = (): CanonicalTrendDescriptor => ({
  descriptor_version: "v2",
  descriptor_state: "unavailable" as const,
  trend_label: null,
  direction: null,
  confidence_score: null,
  dominant_measure_family: "none",
  selected_lookback_points: null,
  observed_on: null,
  reason_code: "missing_canonical_descriptor",
});

const defaultObservationAsOfTrendDescriptor = (): CanonicalTrendDescriptor => ({
  descriptor_version: "v2",
  descriptor_state: "unavailable" as const,
  trend_label: null,
  direction: null,
  confidence_score: null,
  dominant_measure_family: "none",
  selected_lookback_points: null,
  observed_on: null,
  reason_code: "missing_observation_asof_descriptor",
});

const normalizeSummaryCanonicalTrendDescriptor = (
  descriptor: unknown,
): CanonicalTrendDescriptor => {
  if (!descriptor || typeof descriptor !== "object") {
    return defaultCanonicalTrendDescriptor();
  }
  const payload = descriptor as Record<string, unknown>;
  const state = payload.descriptor_state;
  const descriptorState = state === "available" || state === "unavailable" ? state : "unavailable";
  const confidenceCandidate =
    typeof payload.confidence_score === "number" &&
    Number.isFinite(payload.confidence_score) &&
    payload.confidence_score >= 0 &&
    payload.confidence_score <= 1
      ? payload.confidence_score
      : null;
  return {
    descriptor_version: payload.descriptor_version === "v2" ? "v2" : "v2",
    descriptor_state: descriptorState,
    trend_label: typeof payload.trend_label === "string" ? payload.trend_label : null,
    direction:
      descriptorState === "available" &&
      (payload.direction === "up" || payload.direction === "down" || payload.direction === "flat")
        ? payload.direction
        : null,
    confidence_score: descriptorState === "available" ? confidenceCandidate : null,
    dominant_measure_family:
      payload.dominant_measure_family === "theil_sen" ||
      payload.dominant_measure_family === "mixed" ||
      payload.dominant_measure_family === "none"
        ? payload.dominant_measure_family
        : "none",
    selected_lookback_points: isLookbackPoints(payload.selected_lookback_points)
      ? payload.selected_lookback_points
      : null,
    observed_on: typeof payload.observed_on === "string" ? payload.observed_on : null,
    reason_code: typeof payload.reason_code === "string" ? payload.reason_code : null,
  };
};

const normalizeObservationAsOfTrendDescriptor = (descriptor: unknown): CanonicalTrendDescriptor => {
  if (!descriptor || typeof descriptor !== "object") {
    return defaultObservationAsOfTrendDescriptor();
  }
  const payload = descriptor as Record<string, unknown>;
  const state = payload.descriptor_state;
  const descriptorState = state === "available" || state === "unavailable" ? state : "unavailable";
  const confidenceCandidate =
    typeof payload.confidence_score === "number" &&
    Number.isFinite(payload.confidence_score) &&
    payload.confidence_score >= 0 &&
    payload.confidence_score <= 1
      ? payload.confidence_score
      : null;
  return {
    descriptor_version: payload.descriptor_version === "v2" ? "v2" : "v2",
    descriptor_state: descriptorState,
    trend_label: typeof payload.trend_label === "string" ? payload.trend_label : null,
    direction:
      descriptorState === "available" &&
      (payload.direction === "up" || payload.direction === "down" || payload.direction === "flat")
        ? payload.direction
        : null,
    confidence_score: descriptorState === "available" ? confidenceCandidate : null,
    dominant_measure_family:
      payload.dominant_measure_family === "theil_sen" ||
      payload.dominant_measure_family === "mixed" ||
      payload.dominant_measure_family === "none"
        ? payload.dominant_measure_family
        : "none",
    selected_lookback_points: isLookbackPoints(payload.selected_lookback_points)
      ? payload.selected_lookback_points
      : null,
    observed_on: typeof payload.observed_on === "string" ? payload.observed_on : null,
    reason_code: typeof payload.reason_code === "string" ? payload.reason_code : null,
  };
};

const normalizeDatasetSummary = <T extends { canonical_trend_descriptor?: unknown }>(item: T) => ({
  ...item,
  canonical_trend_descriptor: normalizeSummaryCanonicalTrendDescriptor(
    item.canonical_trend_descriptor,
  ),
});

export const fetchDatasetSearch = async (params: {
  q?: string;
  page?: number;
  pageSize?: number;
}): Promise<DatasetSearchResponse> => {
  const query: Record<string, string> = {};

  if (params.q) {
    query.q = params.q;
  }
  appendPaginationQueryParams(query, params);

  const response = await fetch(createUrl("/api/datasets/search", query));
  const payload = await parseResponse<DatasetSearchResponse>(response);
  return {
    ...payload,
    items: payload.items.map((item) => normalizeDatasetSummary(item)),
  };
};

export const fetchSearchSummary = async (): Promise<SearchScopeSummaryResponse> => {
  const response = await fetch(createUrl("/api/datasets/search/summary"));
  return parseResponse<SearchScopeSummaryResponse>(response);
};

export const fetchSearchSuggestions = async (params: {
  q: string;
  limit?: number;
}): Promise<DatasetSearchSuggestionsResponse> => {
  const query: Record<string, string> = { q: params.q };

  if (params.limit) {
    query.limit = String(params.limit);
  }

  const response =
    typeof window === "undefined"
      ? await fetch(createUrl("/api/datasets/search/suggestions", query))
      : await fetch(`/api/datasets/search/suggestions?${new URLSearchParams(query).toString()}`);
  return parseResponse<DatasetSearchSuggestionsResponse>(response);
};

export const fetchRecentDatasets = async (params?: {
  limit?: number;
}): Promise<DatasetRecentUpdatesResponse> => {
  const query: Record<string, string> = {};

  if (params?.limit) {
    query.limit = String(params.limit);
  }

  const response = await fetch(createUrl("/api/datasets/recent", query));
  const payload = await parseResponse<DatasetRecentUpdatesResponse>(response);

  return {
    ...payload,
    items: payload.items.map((item) => {
      const encodedId = encodeURIComponent(item.dataset_id);
      if (item.item_type === "trend_event") {
        return {
          ...item,
          action_links: {
            view_table_href: item.action_links?.view_table_href ?? `/datasets/${encodedId}`,
            download_csv_href:
              item.action_links?.download_csv_href ?? `/api/datasets/${encodedId}.csv`,
          },
        };
      }

      return {
        ...item,
        item_type: "dataset_update" as const,
        description: item.description ?? null,
        geographic_scope: item.geographic_scope ?? null,
        topic_tags: item.topic_tags ?? [],
        canonical_trend_descriptor: normalizeSummaryCanonicalTrendDescriptor(
          item.canonical_trend_descriptor,
        ),
        action_links: {
          view_table_href: item.action_links?.view_table_href ?? `/datasets/${encodedId}`,
          download_csv_href:
            item.action_links?.download_csv_href ?? `/api/datasets/${encodedId}.csv`,
        },
      };
    }),
  };
};

export const fetchDatasetCatalog = async (params: {
  q?: string;
  groupBySource?: boolean;
  source?: string;
  category?: string;
  subscribedOnly?: boolean;
  sort?: string;
  page?: number;
  pageSize?: number;
}): Promise<DatasetCatalogResponse> => {
  const query: Record<string, string> = {};

  if (params.q) {
    query.q = params.q;
  }

  if (params.groupBySource) {
    query.group_by_source = "true";
  }

  if (params.source) {
    query.source = params.source;
  }

  if (params.category) {
    query.category = params.category;
  }

  if (params.subscribedOnly) {
    query.subscribed_only = "true";
  }

  if (params.sort) {
    query.sort = params.sort;
  }
  appendPaginationQueryParams(query, params);

  const response = await fetch(createUrl("/api/datasets", query));
  const payload = await parseResponse<DatasetCatalogResponse>(response);
  return {
    ...payload,
    items: payload.items.map((item) => normalizeDatasetSummary(item)),
  };
};

export const fetchDatasetDetail = async (datasetId: string): Promise<DatasetDetail> => {
  const response =
    typeof window === "undefined"
      ? await fetch(createUrl(`/api/datasets/${encodeURIComponent(datasetId)}`))
      : await fetch(`/api/datasets/${encodeURIComponent(datasetId)}`);
  const payload = await parseResponse<DatasetDetail>(response);
  return {
    ...payload,
    observations: payload.observations.map((observation) => ({
      ...observation,
      as_of_trend_descriptor: normalizeObservationAsOfTrendDescriptor(
        observation.as_of_trend_descriptor,
      ),
    })),
    lookback_trend_evidence: payload.lookback_trend_evidence ?? [],
  };
};

export const fetchDatasetDetailAsOfTrend = async (
  datasetId: string,
  asOfObservedOn: string,
): Promise<DatasetAsOfTrendResponse> => {
  const response = await fetch(
    createUrl(`/api/datasets/${encodeURIComponent(datasetId)}/observations/as-of`, {
      as_of_observed_on: asOfObservedOn,
    }),
  );
  const payload = await parseResponse<DatasetAsOfTrendResponse>(response);
  return {
    ...payload,
    canonical_trend_descriptor: normalizeObservationAsOfTrendDescriptor(
      payload.canonical_trend_descriptor,
    ),
    lookback_trend_evidence: payload.lookback_trend_evidence ?? [],
  };
};

export const fetchSourceList = async (): Promise<SourceListResponse> => {
  const response = await fetch(createUrl("/api/sources"));
  return parseResponse<SourceListResponse>(response);
};

export const fetchSourceDetail = async (
  sourceId: string,
  params?: { page?: number; pageSize?: number },
): Promise<SourceDetail> => {
  const query: Record<string, string> = {};
  appendPaginationQueryParams(query, params ?? {});
  const response = await fetch(createUrl(`/api/sources/${encodeURIComponent(sourceId)}`, query));
  return parseResponse<SourceDetail>(response);
};

export const fetchTopicDetail = async (
  topicId: string,
  params?: { page?: number; pageSize?: number },
): Promise<TopicDetail> => {
  const query: Record<string, string> = {};
  appendPaginationQueryParams(query, params ?? {});
  const response = await fetch(createUrl(`/api/topics/${encodeURIComponent(topicId)}`, query));
  return parseResponse<TopicDetail>(response);
};

export const fetchGeographyDetail = async (
  geographyId: string,
  params?: { page?: number; pageSize?: number },
): Promise<GeographyDetail> => {
  const query: Record<string, string> = {};
  appendPaginationQueryParams(query, params ?? {});
  const response = await fetch(
    createUrl(`/api/geographies/${encodeURIComponent(geographyId)}`, query),
  );
  return parseResponse<GeographyDetail>(response);
};
