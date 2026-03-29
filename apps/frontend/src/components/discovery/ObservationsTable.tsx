"use client";

import { Card } from "@heroui/react/card";
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
    <Card
      className="grid gap-3 border border-(--shell-border) bg-(--shell-surface) p-4 shadow-sm"
      data-testid="observations-table-wrap"
      variant="default"
    >
      <h2 className="pl-1.5">Observed Values</h2>
      <table
        className="w-full border-collapse border border-(--shell-border) bg-transparent"
        data-testid="observations-table"
      >
        <thead>
          <tr>
            <th
              className="border-(--shell-border) border-b px-[0.58rem] py-[0.58rem] text-left"
              scope="col"
            >
              Date of Observation
            </th>
            <th
              className="border-(--shell-border) border-b px-[0.58rem] py-[0.58rem] text-left"
              scope="col"
            >
              Value
            </th>
            <th
              className="border-(--shell-border) border-b px-[0.58rem] py-[0.58rem] text-left"
              scope="col"
            >
              Weekly Change
            </th>
          </tr>
        </thead>
        <tbody>
          {visibleRows.map((row) => (
            <tr key={row.observedOn}>
              <td className="border-(--shell-border) border-b px-[0.58rem] py-[0.58rem] text-left">
                {row.observedOn}
              </td>
              <td className="border-(--shell-border) border-b px-[0.58rem] py-[0.58rem] text-left">
                {row.valueDisplay}
              </td>
              <td
                className={`observations-weekly-change observations-weekly-change-${row.movementState} border-(--shell-border) border-b px-[0.58rem] py-[0.58rem] text-left`}
              >
                {row.weeklyChangeDisplay}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {hasMoreRows ? (
        <button
          className="mx-auto border border-(--shell-border) bg-(--shell-surface) px-[0.9rem] py-[0.42rem] text-[0.73rem] tracking-[0.08em]"
          data-testid="observations-load-archive"
          onClick={() => {
            setShowAll(true);
          }}
          type="button"
        >
          LOAD ARCHIVE ({rows.length} ROWS)
        </button>
      ) : null}
    </Card>
  );
};
