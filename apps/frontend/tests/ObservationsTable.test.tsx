import React from "react";
import { describe, expect, it } from "vitest";
import { ObservationsTable } from "../src/components/discovery/ObservationsTable";
import { renderMarkup } from "./test-utils";

describe("ObservationsTable", () => {
  it("renders table rows for observations", () => {
    const markup = renderMarkup(
      <ObservationsTable
        observations={[
          {
            observed_on: "2026-01-01",
            value: 4.1,
            reported_at: "2026-01-10T00:00:00Z",
            attributes: { revision: 0 },
          },
        ]}
      />,
    );

    expect(markup).toContain("<table");
    expect(markup).toContain("2026-01-01");
    expect(markup).toContain("4.1");
    expect(markup).toContain("Dataset observations");
  });

  it("renders empty state when no observations", () => {
    const markup = renderMarkup(<ObservationsTable observations={[]} />);

    expect(markup).toContain("No observation data available");
    expect(markup).not.toContain("<table");
  });
});
