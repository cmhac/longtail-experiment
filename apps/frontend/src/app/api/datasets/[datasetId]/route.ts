import { type NextRequest, NextResponse } from "next/server";

const getDiscoveryApiBaseUrl = (): string => {
  const value = process.env.DISCOVERY_API_BASE_URL;

  if (!value) {
    throw new Error("Missing DISCOVERY_API_BASE_URL");
  }

  return value.replace(/\/$/, "");
};

interface DatasetCsvRouteContext {
  params: Promise<Record<string, string | string[] | undefined>>;
}

export const GET = async (
  request: NextRequest,
  context: DatasetCsvRouteContext,
): Promise<NextResponse> => {
  try {
    const params = await context.params;
    const datasetIdValue = params.datasetId;
    const datasetIdWithExtension = Array.isArray(datasetIdValue)
      ? datasetIdValue[0]
      : datasetIdValue;

    if (!datasetIdWithExtension || !datasetIdWithExtension.endsWith(".csv")) {
      return NextResponse.json(
        {
          error: {
            code: "not_found",
            message: "Endpoint not found",
          },
        },
        { status: 404 },
      );
    }

    const datasetId = datasetIdWithExtension.slice(0, -".csv".length);
    const backendBaseUrl = getDiscoveryApiBaseUrl();
    const query = request.nextUrl.searchParams.toString();
    const target = `${backendBaseUrl}/api/datasets/${encodeURIComponent(datasetId)}.csv${
      query ? `?${query}` : ""
    }`;

    const response = await fetch(target, {
      method: "GET",
      cache: "no-store",
      headers: {
        accept: "text/csv",
      },
    });

    const body = await response.text();

    return new NextResponse(body, {
      status: response.status,
      headers: {
        "content-type": response.headers.get("content-type") ?? "text/csv; charset=utf-8",
        "content-disposition":
          response.headers.get("content-disposition") ?? `attachment; filename="${datasetId}.csv"`,
      },
    });
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "http_error",
          message: "Unable to fetch dataset CSV",
        },
      },
      { status: 502 },
    );
  }
};
