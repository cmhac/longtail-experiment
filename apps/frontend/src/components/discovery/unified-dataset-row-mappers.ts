import type {
  DatasetRecentItem,
  DatasetSummary,
  TrendRecentItem,
} from "../../lib/api/discovery-types";
import type { UnifiedDatasetRowProps } from "./UnifiedDatasetRow";

const formatDate = (value: string): string => {
  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleDateString("en-US", {
    day: "2-digit",
    month: "short",
    timeZone: "UTC",
    year: "numeric",
  });
};

const normalizeTags = (tags: string[]): string[] => {
  return tags.map((tag) => tag.trim()).filter((tag) => tag.length > 0);
};

const escapeRegExp = (value: string): string => {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
};

const stripGeographyFromDescription = (description: string, geographicScope: string): string => {
  const pattern = new RegExp(`\\s*geography:\\s*${escapeRegExp(geographicScope)}\\.?`, "gi");
  return description.replace(pattern, "").replace(/\s+/g, " ").trim();
};

export const toUnifiedRecentUpdatesRow = (item: DatasetRecentItem): UnifiedDatasetRowProps => {
  const summaryText =
    item.description && item.geographic_scope
      ? stripGeographyFromDescription(item.description, item.geographic_scope)
      : (item.description ?? undefined);

  return {
    datasetId: item.dataset_id,
    destinationHref: `/datasets/${encodeURIComponent(item.dataset_id)}`,
    emphasizedPills: item.geographic_scope ? [item.geographic_scope] : [],
    interactionMode: "row_link",
    sourceLabel: item.source.name.toUpperCase(),
    tagPills: normalizeTags(item.topic_tags),
    title: item.title,
    updatedLabel: formatDate(item.latest_update_at),
    ...(item.canonical_trend_descriptor
      ? { trendDescriptor: item.canonical_trend_descriptor }
      : {}),
    ...(summaryText ? { summaryText } : {}),
  };
};

export const toUnifiedTrendUpdatesRow = (item: TrendRecentItem): UnifiedDatasetRowProps => {
  return {
    datasetId: item.dataset_id,
    destinationHref: `/datasets/${encodeURIComponent(item.dataset_id)}`,
    emphasizedPills: [item.direction.toUpperCase()],
    interactionMode: "row_link",
    sourceLabel: "TREND EVENT",
    summaryText: item.strength,
    tagPills: [item.source.name, `Start ${item.start_period}`],
    title: item.title,
    updatedLabel: formatDate(item.latest_update_at),
  };
};

export const toUnifiedCatalogRow = (item: DatasetSummary): UnifiedDatasetRowProps => {
  const summaryText =
    item.description && item.geographic_scope
      ? stripGeographyFromDescription(item.description, item.geographic_scope)
      : (item.description ?? "No summary available.");

  return {
    datasetId: item.dataset_id,
    destinationHref: `/datasets/${encodeURIComponent(item.dataset_id)}`,
    emphasizedPills: item.geographic_scope ? [item.geographic_scope] : [],
    interactionMode: "title_link",
    sourceLabel: item.source.name.toUpperCase(),
    summaryText,
    tagPills: normalizeTags(item.topic_tags),
    title: item.title,
    updatedLabel: formatDate(item.latest_update_at),
    ...(item.canonical_trend_descriptor
      ? { trendDescriptor: item.canonical_trend_descriptor }
      : {}),
  };
};
