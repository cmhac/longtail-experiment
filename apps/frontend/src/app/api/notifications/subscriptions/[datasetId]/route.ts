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

interface NotificationSubscriptionDeleteRouteContext {
  params: Promise<{ datasetId: string }>;
}

export const DELETE = async (
  request: NextRequest,
  context: NotificationSubscriptionDeleteRouteContext,
): Promise<NextResponse> => {
  try {
    const { datasetId } = await context.params;
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const response = await fetch(
      `${backendBaseUrl}/api/notifications/subscriptions/${encodeURIComponent(datasetId)}`,
      {
        method: "DELETE",
        cache: "no-store",
        headers: {
          accept: "application/json",
          ...forwardAuthHeader(request),
        },
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
          message: "Unable to delete notification subscription",
        },
      },
      { status: 502 },
    );
  }
};
