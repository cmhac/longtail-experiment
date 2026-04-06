import {
  AuthManagementApiError,
  fetchCurrentSessions,
} from "./auth-management-client";
import type {
  CreateSubscriptionRequest,
  DeleteSubscriptionResponse,
  MarkAllReadResponse,
  MarkReadResponse,
  MarkUnreadResponse,
  NotificationApiErrorEnvelope,
  NotificationListResponse,
  NotificationSummaryResponse,
  SubscriptionListResponse,
  SubscriptionResponse,
} from "./notification-types";

export class NotificationApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(message: string, status: number, code = "http_error") {
    super(message);
    this.name = "NotificationApiError";
    this.status = status;
    this.code = code;
  }
}

const getApiBaseUrl = (): string => {
  const value = process.env.DISCOVERY_API_BASE_URL;
  if (value) {
    return value.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    return "";
  }
  throw new Error("Missing DISCOVERY_API_BASE_URL");
};

const createUrl = (path: string): string => `${getApiBaseUrl()}${path}`;

const parseResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    let code = "http_error";
    let message = `Request failed with status ${response.status}`;

    try {
      const payload = (await response.json()) as NotificationApiErrorEnvelope;
      code = payload.error?.code ?? code;
      message = payload.error?.message ?? message;
    } catch {
      // Keep fallback values for non-JSON responses.
    }

    throw new NotificationApiError(message, response.status, code);
  }

  if (response.status === 204 || response.status === 205) {
    return undefined as T;
  }

  return (await response.json()) as T;
};

const withAuthHeaders = (sessionToken?: string): HeadersInit => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (sessionToken) {
    headers.Authorization = `Bearer ${sessionToken}`;
  }

  return headers;
};

const queryValue = (value: string | undefined): string => {
  return value ?? "";
};

export const fetchNotificationList = async (
  sessionToken: string,
  params?: {
    pageSize?: number;
    cursor?: string;
    unreadOnly?: boolean;
  },
): Promise<NotificationListResponse> => {
  const searchParams = new URLSearchParams();
  if (params?.pageSize !== undefined) {
    searchParams.set("page_size", String(params.pageSize));
  }
  if (params?.cursor) {
    searchParams.set("cursor", params.cursor);
  }
  if (params?.unreadOnly !== undefined) {
    searchParams.set("unread_only", params.unreadOnly ? "true" : "false");
  }

  const query = searchParams.toString();
  const response = await fetch(
    createUrl(`/api/notifications${query ? `?${query}` : ""}`),
    {
      method: "GET",
      headers: withAuthHeaders(sessionToken),
      cache: "no-store",
    },
  );
  return parseResponse<NotificationListResponse>(response);
};

export const fetchNotificationSummary = async (
  sessionToken: string,
): Promise<NotificationSummaryResponse> => {
  const response = await fetch(createUrl("/api/notifications/summary"), {
    method: "GET",
    headers: withAuthHeaders(sessionToken),
    cache: "no-store",
  });
  return parseResponse<NotificationSummaryResponse>(response);
};

export const markAllNotificationsRead = async (
  sessionToken: string,
): Promise<MarkAllReadResponse> => {
  const response = await fetch(createUrl("/api/notifications/mark-all-read"), {
    method: "POST",
    headers: withAuthHeaders(sessionToken),
  });
  return parseResponse<MarkAllReadResponse>(response);
};

export const markNotificationRead = async (
  sessionToken: string,
  notificationId: string,
): Promise<MarkReadResponse> => {
  const response = await fetch(
    createUrl(`/api/notifications/${encodeURIComponent(notificationId)}/mark-read`),
    {
      method: "POST",
      headers: withAuthHeaders(sessionToken),
    },
  );
  return parseResponse<MarkReadResponse>(response);
};

export const markNotificationUnread = async (
  sessionToken: string,
  notificationId: string,
): Promise<MarkUnreadResponse> => {
  const response = await fetch(
    createUrl(`/api/notifications/${encodeURIComponent(notificationId)}/mark-unread`),
    {
      method: "POST",
      headers: withAuthHeaders(sessionToken),
    },
  );
  return parseResponse<MarkUnreadResponse>(response);
};

export const fetchNotificationSubscriptions = async (
  sessionToken: string,
): Promise<SubscriptionListResponse> => {
  const response = await fetch(createUrl("/api/notifications/subscriptions"), {
    method: "GET",
    headers: withAuthHeaders(sessionToken),
    cache: "no-store",
  });
  return parseResponse<SubscriptionListResponse>(response);
};

export const createNotificationSubscription = async (
  sessionToken: string,
  payload: CreateSubscriptionRequest,
): Promise<SubscriptionResponse> => {
  const response = await fetch(createUrl("/api/notifications/subscriptions"), {
    method: "POST",
    headers: withAuthHeaders(sessionToken),
    body: JSON.stringify(payload),
  });
  return parseResponse<SubscriptionResponse>(response);
};

export const deleteNotificationSubscription = async (
  sessionToken: string,
  datasetId: string,
): Promise<DeleteSubscriptionResponse> => {
  const response = await fetch(
    createUrl(`/api/notifications/subscriptions/${encodeURIComponent(datasetId)}`),
    {
      method: "DELETE",
      headers: withAuthHeaders(sessionToken),
    },
  );
  return parseResponse<DeleteSubscriptionResponse>(response);
};

export const requireNotificationSessionToken = async (
  sessionToken: string | null | undefined,
): Promise<string> => {
  const token = queryValue(sessionToken ?? undefined).trim();
  if (token === "") {
    throw new AuthManagementApiError("Authentication required", 401, "unauthorized");
  }
  await fetchCurrentSessions(token);
  return token;
};
