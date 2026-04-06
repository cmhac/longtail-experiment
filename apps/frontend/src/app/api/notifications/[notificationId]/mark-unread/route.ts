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

interface NotificationMarkUnreadRouteContext {
  params: Promise<{ notificationId: string }>;
}

export const POST = async (
  request: NextRequest,
  context: NotificationMarkUnreadRouteContext,
): Promise<NextResponse> => {
  try {
    const { notificationId } = await context.params;
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const response = await fetch(
      `${backendBaseUrl}/api/notifications/${encodeURIComponent(notificationId)}/mark-unread`,
      {
        method: "POST",
        cache: "no-store",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
          ...forwardAuthHeader(request),
        },
        body: "{}",
      },
    );
    const body = await response.text();
    return new NextResponse(body, {
      status: response.status,
      headers: {
        "content-type": response.headers.get("content-type") ?? "application/json",
      },
    });
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "http_error",
          message: "Unable to mark notification as unread",
        },
      },
      { status: 502 },
    );
  }
};
