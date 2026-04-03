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

export const POST = async (request: NextRequest): Promise<NextResponse> => {
  try {
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const payload = await request.text();
    const response = await fetch(`${backendBaseUrl}/api/account/password`, {
      method: "POST",
      cache: "no-store",
      headers: {
        "content-type": "application/json",
        accept: "application/json",
        ...forwardAuthHeader(request),
      },
      body: payload,
    });

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

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
          message: "Unable to change account password",
        },
      },
      { status: 502 },
    );
  }
};
