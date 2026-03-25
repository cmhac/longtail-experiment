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
  return (
    <article className="discovery-dataset-card" data-testid="dataset-card">
      <h3>
        <Link href={`/datasets/${item.dataset_id}`}>{item.title}</Link>
      </h3>
      <p>{item.source.name}</p>
      <p>Updated {formatDate(item.latest_update_at)}</p>
    </article>
  );
};
