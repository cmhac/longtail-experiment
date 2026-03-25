import React from "react";
import type { JSX } from "react";
import type { DatasetSummary } from "../../lib/api/discovery-types";
import { UnifiedDatasetRow } from "./UnifiedDatasetRow";
import { toUnifiedCatalogRow } from "./unified-dataset-row-mappers";

interface DatasetCardProps {
  item: DatasetSummary;
}

export const DatasetCard = ({ item }: DatasetCardProps): JSX.Element => {
  return <UnifiedDatasetRow {...toUnifiedCatalogRow(item)} />;
};
