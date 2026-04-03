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
    const response = await fetch(`${backendBaseUrl}/api/account/profile`, {
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
          message: "Unable to fetch account profile",
        },
      },
      { status: 502 },
    );
  }
};

export const PATCH = async (request: NextRequest): Promise<NextResponse> => {
  try {
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const payload = await request.text();
    const response = await fetch(`${backendBaseUrl}/api/account/profile`, {
      method: "PATCH",
      cache: "no-store",
      headers: {
        "content-type": "application/json",
        accept: "application/json",
        ...forwardAuthHeader(request),
      },
      body: payload,
    });
    return passthroughJsonResponse(response);
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "http_error",
          message: "Unable to update account profile",
        },
      },
      { status: 502 },
    );
  }
};
