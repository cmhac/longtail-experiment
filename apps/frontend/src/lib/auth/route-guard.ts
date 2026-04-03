import { type AuthSessionState, loadAuthSessionState } from "./session-state";

const LOGIN_PATH = "/login";
const DEFAULT_POST_LOGIN_PATH = "/comparison";

export interface ProtectedRouteDecision {
  allow: boolean;
  redirectTo: string | null;
  session: AuthSessionState | null;
}

const normalizeProtectedPath = (pathname: string): string => {
  const normalized = pathname.trim();
  if (normalized === "" || normalized === LOGIN_PATH) {
    return DEFAULT_POST_LOGIN_PATH;
  }
  return normalized.startsWith("/") ? normalized : `/${normalized}`;
};

export const buildLoginRedirectPath = (pathname: string): string => {
  const protectedPath = normalizeProtectedPath(pathname);
  return `${LOGIN_PATH}?next=${encodeURIComponent(protectedPath)}`;
};

export const resolvePostLoginRedirect = (nextPath: string | null): string => {
  if (!nextPath || !nextPath.startsWith("/") || nextPath.startsWith("//")) {
    return DEFAULT_POST_LOGIN_PATH;
  }
  if (nextPath === LOGIN_PATH) {
    return DEFAULT_POST_LOGIN_PATH;
  }
  return nextPath;
};

export const evaluateProtectedRoute = (
  pathname: string,
  session: AuthSessionState | null = loadAuthSessionState(),
): ProtectedRouteDecision => {
  if (session) {
    return { allow: true, redirectTo: null, session };
  }

  return {
    allow: false,
    redirectTo: buildLoginRedirectPath(pathname),
    session: null,
  };
};
