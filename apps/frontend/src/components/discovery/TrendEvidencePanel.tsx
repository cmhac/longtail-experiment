"use client";

import React from "react";
import type { JSX } from "react";

import type { LookbackTrendSnapshot } from "../../lib/api/discovery-types";

interface TrendEvidencePanelProps {
  snapshots: LookbackTrendSnapshot[];
  testId?: string;
}

export const TrendEvidencePanel = ({
  snapshots,
  testId = "trend-evidence-panel",
}: TrendEvidencePanelProps): JSX.Element => {
  return (
    <details data-testid={testId} className="p-3">
      <summary className="cursor-pointer font-medium text-sm">Trend evidence details</summary>
      <div className="mt-3 space-y-2" data-testid={`${testId}-content`}>
        {snapshots.map((snapshot) => (
          <div
            key={`${snapshot.lookback_points}-${snapshot.applicability_state}`}
            className="text-sm"
            data-testid={`${testId}-row`}
          >
            <span className="font-medium">{snapshot.lookback_points}</span>
            <span className="ml-2">{snapshot.applicability_state}</span>
            <span className="ml-2">{snapshot.direction ?? "unavailable"}</span>
          </div>
        ))}
      </div>
    </details>
  );
};
