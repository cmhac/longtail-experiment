import { type NextRequest, NextResponse } from "next/server";

const getDiscoveryApiBaseUrl = (): string => {
  const value = process.env.DISCOVERY_API_BASE_URL;
  if (!value) {
    throw new Error("Missing DISCOVERY_API_BASE_URL");
  }
  return value.replace(/\/$/, "");
};

const forwardAuthHeader = (request: NextRequest): Record<string, string> => {
  const authorization = request.headers.get("authorization");
  return authorization ? { authorization } : {};
};

const passthroughJsonResponse = async (response: Response): Promise<NextResponse> => {
  const body = await response.text();
  return new NextResponse(body, {
    status: response.status,
    headers: {
      "content-type": response.headers.get("content-type") ?? "application/json",
    },
  });
};

export const GET = async (request: NextRequest): Promise<NextResponse> => {
  try {
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const response = await fetch(`${backendBaseUrl}/api/admin/users`, {
      method: "GET",
      cache: "no-store",
      headers: {
        accept: "application/json",
        ...forwardAuthHeader(request),
      },
    });
    return passthroughJsonResponse(response);
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "http_error",
          message: "Unable to list admin users",
        },
      },
      { status: 502 },
    );
  }
};

export const PATCH = async (request: NextRequest): Promise<NextResponse> => {
  try {
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const payload = (await request.json()) as {
      user_id?: string;
      account_status?: "active" | "deactivated";
      role_action?: "grant_admin" | "revoke_admin";
    };
    const userId = String(payload.user_id ?? "").trim();

    if (userId === "") {
      return NextResponse.json(
        {
          error: {
            code: "invalid_request",
            message: "user_id is required",
          },
        },
        { status: 400 },
      );
    }

    const hasRoleAction =
      payload.role_action === "grant_admin" || payload.role_action === "revoke_admin";
    const route = hasRoleAction
      ? `${backendBaseUrl}/api/admin/users/${encodeURIComponent(userId)}/role`
      : `${backendBaseUrl}/api/admin/users/${encodeURIComponent(userId)}/status`;
    const bodyPayload = hasRoleAction
      ? { role_action: payload.role_action }
      : { account_status: payload.account_status };

    const response = await fetch(route, {
      method: "PATCH",
      cache: "no-store",
      headers: {
        "content-type": "application/json",
        accept: "application/json",
        ...forwardAuthHeader(request),
      },
      body: JSON.stringify(bodyPayload),
    });

    return passthroughJsonResponse(response);
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "http_error",
          message: "Unable to update user status",
        },
      },
      { status: 502 },
    );
  }
};

export const POST = async (request: NextRequest): Promise<NextResponse> => {
  try {
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const payload = (await request.json()) as { action?: string; user_id?: string };
    const action = String(payload.action ?? "")
      .trim()
      .toLowerCase();
    const userId = String(payload.user_id ?? "").trim();

    if (action !== "revoke_sessions" || userId === "") {
      return NextResponse.json(
        {
          error: {
            code: "invalid_request",
            message: "action must be revoke_sessions and user_id is required",
          },
        },
        { status: 400 },
      );
    }

    const response = await fetch(
      `${backendBaseUrl}/api/admin/users/${encodeURIComponent(userId)}/sessions/revoke`,
      {
        method: "POST",
        cache: "no-store",
        headers: {
          "content-type": "application/json",
          accept: "application/json",
          ...forwardAuthHeader(request),
        },
      },
    );

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    return passthroughJsonResponse(response);
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "http_error",
          message: "Unable to revoke user sessions",
        },
      },
      { status: 502 },
    );
  }
};
