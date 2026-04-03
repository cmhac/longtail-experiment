import type {
  AccountNavigationResponse,
  AdminNavigationResponse,
  AdminUserListResponse,
  AdminUserSummary,
  AuthErrorEnvelope,
  AuthSessionResponse,
  ChangePasswordRequest,
  DeletionRequestResponse,
  LoginRequest,
  ProfileResponse,
  RegisterRequest,
  SessionListResponse,
  UpdateProfileRequest,
  UpdateUserRoleRequest,
  UpdateUserStatusRequest,
} from "./auth-management-types";

export class AuthManagementApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(message: string, status: number, code = "http_error") {
    super(message);
    this.name = "AuthManagementApiError";
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
      const payload = (await response.json()) as AuthErrorEnvelope;
      code = payload.error?.code ?? code;
      message = payload.error?.message ?? message;
    } catch {
      // Keep fallback values for non-JSON responses.
    }

    throw new AuthManagementApiError(message, response.status, code);
  }

  if (response.status === 205) {
    return undefined as T;
  }

  if (response.status === 204) {
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

export const registerAccount = async (payload: RegisterRequest): Promise<AuthSessionResponse> => {
  const response = await fetch(createUrl("/api/auth/sessions"), {
    method: "POST",
    headers: withAuthHeaders(),
    body: JSON.stringify({ action: "register", ...payload }),
  });
  return parseResponse<AuthSessionResponse>(response);
};

export const loginAccount = async (payload: LoginRequest): Promise<AuthSessionResponse> => {
  const response = await fetch(createUrl("/api/auth/sessions"), {
    method: "POST",
    headers: withAuthHeaders(),
    body: JSON.stringify({ action: "login", ...payload }),
  });
  return parseResponse<AuthSessionResponse>(response);
};

export const logoutAccount = async (sessionToken: string): Promise<void> => {
  const response = await fetch(createUrl("/api/auth/sessions"), {
    method: "POST",
    headers: withAuthHeaders(sessionToken),
    body: JSON.stringify({ action: "logout" }),
  });
  await parseResponse<void>(response);
};

export const fetchCurrentSessions = async (sessionToken: string): Promise<SessionListResponse> => {
  const response = await fetch(createUrl("/api/auth/sessions"), {
    method: "GET",
    headers: withAuthHeaders(sessionToken),
  });
  return parseResponse<SessionListResponse>(response);
};

export const revokeSession = async (sessionToken: string, sessionId: string): Promise<void> => {
  const response = await fetch(createUrl("/api/auth/sessions"), {
    method: "POST",
    headers: withAuthHeaders(sessionToken),
    body: JSON.stringify({ action: "revoke", session_id: sessionId }),
  });
  await parseResponse<void>(response);
};

export const fetchAccountProfile = async (sessionToken: string): Promise<ProfileResponse> => {
  const response = await fetch(createUrl("/api/account/profile"), {
    method: "GET",
    headers: withAuthHeaders(sessionToken),
  });
  return parseResponse<ProfileResponse>(response);
};

export const fetchAccountNavigation = async (
  sessionToken: string,
): Promise<AccountNavigationResponse> => {
  const response = await fetch(createUrl("/api/account/navigation"), {
    method: "GET",
    headers: withAuthHeaders(sessionToken),
  });
  return parseResponse<AccountNavigationResponse>(response);
};

export const updateAccountProfile = async (
  sessionToken: string,
  payload: UpdateProfileRequest,
): Promise<ProfileResponse> => {
  const response = await fetch(createUrl("/api/account/profile"), {
    method: "PATCH",
    headers: withAuthHeaders(sessionToken),
    body: JSON.stringify(payload),
  });
  return parseResponse<ProfileResponse>(response);
};

export const changeAccountPassword = async (
  sessionToken: string,
  payload: ChangePasswordRequest,
): Promise<void> => {
  const response = await fetch(createUrl("/api/account/password"), {
    method: "POST",
    headers: withAuthHeaders(sessionToken),
    body: JSON.stringify(payload),
  });
  await parseResponse<void>(response);
};

export const requestAccountDeletion = async (
  sessionToken: string,
): Promise<DeletionRequestResponse> => {
  const response = await fetch(createUrl("/api/account/deletion-request"), {
    method: "POST",
    headers: withAuthHeaders(sessionToken),
  });
  return parseResponse<DeletionRequestResponse>(response);
};

export const fetchAdminUsers = async (sessionToken: string): Promise<AdminUserListResponse> => {
  const response = await fetch(createUrl("/api/admin/users"), {
    method: "GET",
    headers: withAuthHeaders(sessionToken),
  });
  return parseResponse<AdminUserListResponse>(response);
};

export const fetchAdminNavigation = async (
  sessionToken: string,
): Promise<AdminNavigationResponse> => {
  const response = await fetch(createUrl("/api/admin/navigation"), {
    method: "GET",
    headers: withAuthHeaders(sessionToken),
  });
  return parseResponse<AdminNavigationResponse>(response);
};

export const updateAdminUserStatus = async (
  sessionToken: string,
  userId: string,
  payload: UpdateUserStatusRequest,
): Promise<AdminUserSummary> => {
  const response = await fetch(createUrl("/api/admin/users"), {
    method: "PATCH",
    headers: withAuthHeaders(sessionToken),
    body: JSON.stringify({
      user_id: userId,
      account_status: payload.account_status,
    }),
  });
  return parseResponse<AdminUserSummary>(response);
};

export const updateAdminUserRole = async (
  sessionToken: string,
  userId: string,
  payload: UpdateUserRoleRequest,
): Promise<AdminUserSummary> => {
  const response = await fetch(createUrl("/api/admin/users"), {
    method: "PATCH",
    headers: withAuthHeaders(sessionToken),
    body: JSON.stringify({
      user_id: userId,
      role_action: payload.role_action,
    }),
  });
  return parseResponse<AdminUserSummary>(response);
};

export const revokeAdminUserSessions = async (
  sessionToken: string,
  userId: string,
): Promise<void> => {
  const response = await fetch(createUrl("/api/admin/users"), {
    method: "POST",
    headers: withAuthHeaders(sessionToken),
    body: JSON.stringify({
      action: "revoke_sessions",
      user_id: userId,
    }),
  });
  await parseResponse<void>(response);
};
