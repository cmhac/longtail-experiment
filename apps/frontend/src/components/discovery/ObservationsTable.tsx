import React from "react";
import type { JSX } from "react";
import type { ObservationPoint } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";

interface ObservationsTableProps {
  observations: ObservationPoint[];
}

export const ObservationsTable = ({ observations }: ObservationsTableProps): JSX.Element => {
  if (observations.length === 0) {
    return <EmptyState message="No observation data available" />;
  }

  return (
    <table className="discovery-observations-table" data-testid="observations-table">
      <caption>Dataset observations</caption>
      <thead>
        <tr>
          <th scope="col">Observed On</th>
          <th scope="col">Value</th>
        </tr>
      </thead>
      <tbody>
        {observations.map((observation) => (
          <tr key={`${observation.observed_on}-${observation.reported_at}`}>
            <td>{observation.observed_on}</td>
            <td>{observation.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
