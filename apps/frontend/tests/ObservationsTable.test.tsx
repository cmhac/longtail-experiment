/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { ObservationsTable } from "../src/components/discovery/ObservationsTable";
import { buildDatasetDetailFixture } from "./fixtures/dataset-detail-fixtures";
import { renderMarkup } from "./test-utils";

describe("ObservationsTable", () => {
  it("renders table rows for observations", () => {
    const fixture = buildDatasetDetailFixture();
    const markup = renderMarkup(
      <ObservationsTable observations={fixture.observations} unit="$/Gal" defaultVisibleRows={2} />,
    );

    expect(markup).toContain("<table");
    expect(markup).toContain("Jan 15, 2024");
    expect(markup).toContain("Weekly Change");
    expect(markup).not.toContain("Status");
    expect(markup).not.toContain("status");
    expect(markup).not.toContain("Dataset observations");
    expect(markup).toContain('data-testid="observations-load-archive"');
  });

  it("renders empty state when no observations", () => {
    const markup = renderMarkup(<ObservationsTable observations={[]} />);

    expect(markup).toContain("No observation data available");
    expect(markup).not.toContain("<table");
  });

  it("reveals all rows when load archive is clicked", () => {
    const fixture = buildDatasetDetailFixture();
    const extendedObservations = [
      ...fixture.observations,
      {
        observed_on: "2024-01-22",
        value: 3.18,
        reported_at: "2024-01-23T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-01-29",
        value: 3.2,
        reported_at: "2024-01-30T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-02-05",
        value: 3.16,
        reported_at: "2024-02-06T00:00:00Z",
        attributes: {},
      },
      {
        observed_on: "2024-02-12",
        value: 3.22,
        reported_at: "2024-02-13T00:00:00Z",
        attributes: {},
      },
    ];

    render(
      <ObservationsTable observations={extendedObservations} unit="$/Gal" defaultVisibleRows={3} />,
    );

    expect(screen.getAllByRole("row")).toHaveLength(4);
    fireEvent.click(screen.getByTestId("observations-load-archive"));
    expect(screen.getAllByRole("row")).toHaveLength(8);
  });
});
