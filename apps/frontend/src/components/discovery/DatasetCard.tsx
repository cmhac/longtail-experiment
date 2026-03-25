import Link from "next/link";
import React from "react";
import type { JSX } from "react";
import type { DatasetSummary } from "../../lib/api/discovery-types";

interface DatasetCardProps {
  item: DatasetSummary;
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

export const DatasetCard = ({ item }: DatasetCardProps): JSX.Element => {
  const summaryText = item.description ?? "No summary available.";

  return (
    <article className="discovery-dataset-card" data-testid="dataset-card">
      <header className="dataset-card-header">
        <span className="dataset-card-source" data-testid="dataset-card-source">
          {item.source.name}
        </span>
        <p className="dataset-card-updated" data-testid="dataset-card-updated">
          Last updated: {formatDate(item.latest_update_at)}
        </p>
      </header>

      <h3 className="dataset-card-title">
        <Link href={`/datasets/${item.dataset_id}`}>{item.title}</Link>
      </h3>

      <p className="dataset-card-summary" data-testid="dataset-card-summary">
        {summaryText}
      </p>

      <ul className="dataset-card-tags" data-testid="dataset-card-tags">
        {(item.topic_tags ?? []).map((tag) => (
          <li key={`${item.dataset_id}-${tag}`}>
            <span className="dataset-card-tag">{tag}</span>
          </li>
        ))}
      </ul>
    </article>
  );
};
