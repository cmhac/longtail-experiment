export type AccountStatus = "active" | "deactivated" | "deletion_pending" | "deleted";
export type SessionStatus = "active" | "revoked" | "expired";

export interface AuthErrorEnvelope {
  error: {
    code: string;
    message: string;
  };
}

export interface CurrentUserSummary {
  user_id: string;
  email: string;
  display_name: string | null;
  account_status: AccountStatus;
  is_admin: boolean;
}

export interface SessionSummary {
  session_id: string;
  created_at: string;
  expires_at: string;
  session_status: SessionStatus;
  client_label: string | null;
}

export interface AuthSessionResponse {
  user: CurrentUserSummary;
  session: SessionSummary;
}

export interface SessionListResponse {
  items: SessionSummary[];
}

export interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UpdateProfileRequest {
  display_name: string | null;
}

export interface ProfileResponse extends CurrentUserSummary {
  updated_at: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface DeletionRequestResponse {
  user_id: string;
  account_status: AccountStatus;
  deletion_due_at: string;
}

export interface AdminUserSummary {
  user_id: string;
  email: string;
  display_name: string | null;
  account_status: AccountStatus;
  is_admin: boolean;
  updated_at: string;
}

export interface AdminUserListResponse {
  items: AdminUserSummary[];
}

export interface UpdateUserStatusRequest {
  account_status: "active" | "deactivated";
}
