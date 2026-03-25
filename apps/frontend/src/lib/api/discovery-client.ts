import type {
  ApiErrorEnvelope,
  DatasetCatalogResponse,
  DatasetDetail,
  DatasetRecentUpdatesResponse,
  DatasetSearchResponse,
  DatasetSearchSuggestionsResponse,
  SearchScopeSummaryResponse,
} from "./discovery-types";

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

export const fetchDatasetSearch = async (params: {
  q?: string;
  page?: number;
  pageSize?: number;
}): Promise<DatasetSearchResponse> => {
  const query: Record<string, string> = {};

  if (params.q) {
    query.q = params.q;
  }

  if (params.page) {
    query.page = String(params.page);
  }

  if (params.pageSize) {
    query.page_size = String(params.pageSize);
  }

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
  return parseResponse<DatasetRecentUpdatesResponse>(response);
};

export const fetchDatasetCatalog = async (params: {
  q?: string;
  groupBySource?: boolean;
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

  if (params.page) {
    query.page = String(params.page);
  }

  if (params.pageSize) {
    query.page_size = String(params.pageSize);
  }

  const response = await fetch(createUrl("/api/datasets", query));
  return parseResponse<DatasetCatalogResponse>(response);
};

export const fetchDatasetDetail = async (datasetId: string): Promise<DatasetDetail> => {
  const response = await fetch(createUrl(`/api/datasets/${encodeURIComponent(datasetId)}`));
  return parseResponse<DatasetDetail>(response);
};
