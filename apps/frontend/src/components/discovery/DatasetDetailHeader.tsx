import React from "react";
import type { JSX } from "react";
import type { DatasetDetail } from "../../lib/api/discovery-types";

interface DatasetDetailHeaderProps {
  data: DatasetDetail;
}

export const DatasetDetailHeader = ({ data }: DatasetDetailHeaderProps): JSX.Element => {
  return (
    <header className="discovery-dataset-detail-header" data-testid="dataset-detail-header">
      <p>{data.source.name}</p>
      <h1>{data.title}</h1>
      <p>{data.description ?? "No description available"}</p>
      {data.geographic_scope ? <p>Geographic scope: {data.geographic_scope}</p> : null}
      <div aria-label="Topic tags">
        {data.topic_tags.length > 0 ? (
          data.topic_tags.map((tag) => (
            <span key={tag} className="discovery-topic-tag">
              {tag}
            </span>
          ))
        ) : (
          <span>No topic tags</span>
        )}
      </div>
    </header>
  );
};
