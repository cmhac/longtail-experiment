import type { CurrentUserSummary } from "../api/auth-management-types";

export interface AuthSessionState {
  sessionToken: string;
  user: CurrentUserSummary;
  restoredAt: string;
}

const SESSION_STORAGE_KEY = "longtail.auth.session";

const isStorageAvailable = (): boolean => {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
};

export const loadAuthSessionState = (): AuthSessionState | null => {
  if (!isStorageAvailable()) {
    return null;
  }

  const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as AuthSessionState;
    if (!parsed.sessionToken || !parsed.user?.user_id) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
};

export const persistAuthSessionState = (state: AuthSessionState): void => {
  if (!isStorageAvailable()) {
    return;
  }

  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(state));
};

export const clearAuthSessionState = (): void => {
  if (!isStorageAvailable()) {
    return;
  }

  window.localStorage.removeItem(SESSION_STORAGE_KEY);
};
