import { describe, expect, it } from "vitest";
import {
  buildInsightMetrics,
  buildObservationRows,
  filterObservationRange,
  formatObservedOn,
  formatValue,
  getMetadataRows,
} from "../src/components/discovery/dataset-detail-view-model";
import { buildDatasetDetailFixture } from "./fixtures/dataset-detail-fixtures";

describe("dataset-detail-view-model", () => {
  it("formats observed dates for display", () => {
    expect(formatObservedOn("2024-01-15")).toBe("Jan 15, 2024");
  });

  it("formats values with and without slash-prefixed units", () => {
    expect(formatValue(3.2)).toBe("$3.200");
    expect(formatValue(3.2, "$/Gal")).toBe("$3.200 $/Gal");
    expect(formatValue(3.2, "/Gal")).toBe("$3.200/Gal");
  });

  it("builds insight metrics from observation history", () => {
    const metrics = buildInsightMetrics(buildDatasetDetailFixture());
    const latest = metrics[0];
    const high = metrics[1];
    const low = metrics[2];

    expect(latest).toBeDefined();
    expect(high).toBeDefined();
    expect(low).toBeDefined();

    if (!latest || !high || !low) {
      throw new Error("Expected metrics to be present");
    }

    expect(latest.label).toBe("Latest Observation");
    expect(latest.value).toContain("$3.150");
    expect(latest.movementSummary).toContain("+");
    expect(high.label).toBe("1-Year High");
    expect(low.label).toBe("1-Year Low");
  });

  it("builds observation rows in recency order with movement state", () => {
    const rows = buildObservationRows(buildDatasetDetailFixture().observations, "$/Gal");
    const newest = rows[0];
    const middle = rows[1];
    const oldest = rows[2];

    expect(rows).toHaveLength(3);
    expect(newest).toBeDefined();
    expect(middle).toBeDefined();
    expect(oldest).toBeDefined();

    if (!newest || !middle || !oldest) {
      throw new Error("Expected observation rows to be present");
    }

    expect(newest.observedOn).toBe("Jan 15, 2024");
    expect(newest.movementState).toBe("positive");
    expect(middle.movementState).toBe("negative");
    expect(oldest.movementState).toBe("unavailable");
  });

  it("filters observation ranges by control key", () => {
    const observations = buildDatasetDetailFixture().observations;

    expect(filterObservationRange(observations, "1M")).toHaveLength(3);
    expect(filterObservationRange(observations, "ALL")).toHaveLength(3);
  });

  it("returns empty-data insight metrics when observations are missing", () => {
    const metrics = buildInsightMetrics({ ...buildDatasetDetailFixture(), observations: [] });

    expect(metrics[0]?.value).toBe("No data available");
    expect(metrics[1]?.value).toBe("--");
    expect(metrics[2]?.value).toBe("--");
  });

  it("omits movement summary when only one observation exists", () => {
    const fixture = buildDatasetDetailFixture();
    const metrics = buildInsightMetrics({
      ...fixture,
      observations: fixture.observations.slice(0, 1),
    });

    expect(metrics[0]?.movementSummary).toBeUndefined();
    expect(metrics[0]?.movementState).toBeUndefined();
  });

  it("returns metadata rows with fallbacks when metadata fields are missing", () => {
    const rows = getMetadataRows({
      ...buildDatasetDetailFixture(),
      metadata: {
        source_type: null,
        unit: null,
      },
      observations: [],
    });

    expect(rows.some((row) => row.key === "Frequency")).toBe(true);
    expect(rows.some((row) => row.key === "Source Type")).toBe(true);
    expect(rows.every((row) => row.value === "--")).toBe(true);
    expect(rows.some((row) => row.key === "Unit")).toBe(false);
  });

  it("returns all metadata rows when metadata values are present", () => {
    const rows = getMetadataRows(buildDatasetDetailFixture());

    expect(rows.some((row) => row.key === "Frequency")).toBe(true);
    expect(rows.some((row) => row.key === "Source Type")).toBe(true);
    expect(rows.some((row) => row.key === "Unit")).toBe(false);
  });

  it("derives weekly frequency from recent observation spacing", () => {
    const rows = getMetadataRows(buildDatasetDetailFixture());
    const frequency = rows.find((row) => row.key === "Frequency");

    expect(frequency?.value).toBe("Weekly");
  });
});
