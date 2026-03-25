import Link from "next/link";
import React from "react";
import type { JSX } from "react";
import type { DatasetRecentItem } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";

interface RecentUpdatesFeedProps {
  items: DatasetRecentItem[];
  unavailable?: boolean;
}

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

const escapeRegExp = (value: string): string => {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
};

const stripGeographyFromDescription = (description: string, geographicScope: string): string => {
  const pattern = new RegExp(`\\s*geography:\\s*${escapeRegExp(geographicScope)}\\.?`, "gi");
  return description.replace(pattern, "").replace(/\s+/g, " ").trim();
};

export const RecentUpdatesFeed = ({
  items,
  unavailable = false,
}: RecentUpdatesFeedProps): JSX.Element => {
  if (unavailable) {
    return <EmptyState message="Recent updates are temporarily unavailable." />;
  }

  if (items.length === 0) {
    return <EmptyState message="No recent updates." />;
  }

  return (
    <section className="recent-updates-feed" data-testid="recent-updates-feed">
      <header className="recent-updates-header" data-testid="recent-updates-header">
        <h2>Recent Updates</h2>
      </header>
      {items.slice(0, 5).map((item) => {
        const normalizedDescription =
          item.description && item.geographic_scope
            ? stripGeographyFromDescription(item.description, item.geographic_scope)
            : item.description;
        const topicTags = item.topic_tags.map((tag) => tag.trim()).filter((tag) => tag.length > 0);
        const hasPills = Boolean(item.geographic_scope) || topicTags.length > 0;

        return (
          <Link
            className="recent-updates-row"
            data-testid="recent-updates-row"
            href={`/datasets/${encodeURIComponent(item.dataset_id)}`}
            key={item.dataset_id}
          >
            <div className="recent-updates-meta-rail">
              <span className="recent-updates-source">{item.source.name.toUpperCase()}</span>
              <span className="recent-updates-date">{formatDate(item.latest_update_at)}</span>
            </div>
            <div className="recent-updates-body">
              <h3>{item.title}</h3>
              {normalizedDescription ? <p>{normalizedDescription}</p> : null}
              {hasPills ? (
                <div className="recent-updates-pills" data-testid="recent-updates-pills">
                  {item.geographic_scope ? (
                    <span className="recent-updates-pill recent-updates-geography-pill">
                      {item.geographic_scope}
                    </span>
                  ) : null}
                  {topicTags.map((tag) => (
                    <span className="recent-updates-pill" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          </Link>
        );
      })}
    </section>
  );
};
