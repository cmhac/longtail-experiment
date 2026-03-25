export interface SearchParamReader {
  get(name: string): string | null;
}

export const normalizeSearchQuery = (rawQuery: string): string => {
  return rawQuery.trim();
};

export const buildSearchUrl = (pathname: string, rawQuery: string, targetPath?: string): string => {
  const trimmed = normalizeSearchQuery(rawQuery);
  const destination = targetPath ?? pathname;

  if (trimmed.length === 0) {
    return destination;
  }

  const query = new URLSearchParams({ q: trimmed });
  return `${destination}?${query.toString()}`;
};

export const getQueryFromSearchParams = (params: SearchParamReader | null): string => {
  return params?.get("q")?.trim() ?? "";
};
