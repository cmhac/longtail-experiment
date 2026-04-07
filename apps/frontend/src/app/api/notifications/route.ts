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

export const GET = async (request: NextRequest): Promise<NextResponse> => {
  try {
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const query = request.nextUrl.searchParams.toString();
    const response = await fetch(`${backendBaseUrl}/api/notifications${query ? `?${query}` : ""}`, {
      method: "GET",
      cache: "no-store",
      headers: {
        accept: "application/json",
        ...forwardAuthHeader(request),
      },
    });
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
          message: "Unable to fetch notifications",
        },
      },
      { status: 502 },
    );
  }
};
