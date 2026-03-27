import { type NextRequest, NextResponse } from "next/server";

const getDiscoveryApiBaseUrl = (): string => {
  const value = process.env.DISCOVERY_API_BASE_URL;

  if (!value) {
    throw new Error("Missing DISCOVERY_API_BASE_URL");
  }

  return value.replace(/\/$/, "");
};

interface GeographyDetailRouteContext {
  params: Promise<{ geographyId: string }>;
}

export const GET = async (
  request: NextRequest,
  context: GeographyDetailRouteContext,
): Promise<NextResponse> => {
  try {
    const { geographyId } = await context.params;
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const query = request.nextUrl.searchParams.toString();
    const target = `${backendBaseUrl}/api/geographies/${encodeURIComponent(geographyId)}${
      query ? `?${query}` : ""
    }`;

    const response = await fetch(target, {
      method: "GET",
      cache: "no-store",
      headers: {
        accept: "application/json",
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
          message: "Unable to fetch geography details",
        },
      },
      { status: 502 },
    );
  }
};
