"use client";

import React from "react";
import type { JSX } from "react";
import type { ObservationPoint } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";
import { buildObservationRows } from "./dataset-detail-view-model";

interface ObservationsTableProps {
  observations: ObservationPoint[];
  unitType?: string | null;
  unitLabel?: string | null;
  defaultVisibleRows?: number;
}

export const ObservationsTable = ({
  observations,
  unitType,
  unitLabel,
  defaultVisibleRows = 6,
}: ObservationsTableProps): JSX.Element => {
  const [showAll, setShowAll] = React.useState(false);

  if (observations.length === 0) {
    return <EmptyState message="No observation data available" />;
  }

  const rows = buildObservationRows(observations, unitType, unitLabel);
  const visibleRows = showAll ? rows : rows.slice(0, defaultVisibleRows);
  const hasMoreRows = rows.length > defaultVisibleRows;

  return (
    <div className="discovery-observations-table-wrap" data-testid="observations-table-wrap">
      <table className="discovery-observations-table" data-testid="observations-table">
        <thead>
          <tr>
            <th scope="col">Date of Observation</th>
            <th scope="col">Value</th>
            <th scope="col">Weekly Change</th>
          </tr>
        </thead>
        <tbody>
          {visibleRows.map((row) => (
            <tr key={row.observedOn}>
              <td>{row.observedOn}</td>
              <td>{row.valueDisplay}</td>
              <td
                className={`observations-weekly-change observations-weekly-change-${row.movementState}`}
              >
                {row.weeklyChangeDisplay}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {hasMoreRows ? (
        <button
          className="observations-load-archive"
          data-testid="observations-load-archive"
          onClick={() => {
            setShowAll(true);
          }}
          type="button"
        >
          LOAD ARCHIVE ({rows.length} ROWS)
        </button>
      ) : null}
    </div>
  );
};
