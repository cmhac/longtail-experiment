import type {
  ApiErrorEnvelope,
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
  return parseResponse<DatasetSearchResponse>(response);
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
      return {
        ...item,
        description: item.description ?? null,
        geographic_scope: item.geographic_scope ?? null,
        topic_tags: item.topic_tags ?? [],
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

  if (params.sort) {
    query.sort = params.sort;
  }
  appendPaginationQueryParams(query, params);

  const response = await fetch(createUrl("/api/datasets", query));
  return parseResponse<DatasetCatalogResponse>(response);
};

export const fetchDatasetDetail = async (datasetId: string): Promise<DatasetDetail> => {
  const response =
    typeof window === "undefined"
      ? await fetch(createUrl(`/api/datasets/${encodeURIComponent(datasetId)}`))
      : await fetch(`/api/datasets/${encodeURIComponent(datasetId)}`);
  return parseResponse<DatasetDetail>(response);
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
