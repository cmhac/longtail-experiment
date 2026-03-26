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

  it("formats values for usd, percent, and plain number unit types", () => {
    expect(formatValue(3.2)).toBe("$3.200");
    expect(formatValue(3.2, "usd", "$/Gal")).toBe("$3.200 $/Gal");
    expect(formatValue(3.2, "usd", "/Gal")).toBe("$3.200/Gal");
    expect(formatValue(4.33, "percent")).toBe("4.330%");
    expect(formatValue(7.125, "number")).toBe("7.125");
    expect(formatValue(5.1, null, "Percent")).toBe("5.100%");
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

  it("uses selected chart range to set high/low labels and values", () => {
    const fixture = buildDatasetDetailFixture();
    const manyObservations = Array.from({ length: 60 }, (_, index) => {
      const day = String(index + 1).padStart(2, "0");
      return {
        observed_on: `2024-03-${day}`,
        value: index + 1,
        reported_at: `2024-03-${day}T00:00:00Z`,
        attributes: {},
      };
    });

    const monthlyMetrics = buildInsightMetrics(
      {
        ...fixture,
        metadata: { ...fixture.metadata, unit: null, unit_type: "number" },
        observations: manyObservations,
      },
      "1M",
    );
    const allMetrics = buildInsightMetrics(
      {
        ...fixture,
        metadata: { ...fixture.metadata, unit: null, unit_type: "number" },
        observations: manyObservations,
      },
      "ALL",
    );

    expect(monthlyMetrics[1]?.label).toBe("1-Month High");
    expect(monthlyMetrics[2]?.label).toBe("1-Month Low");
    expect(monthlyMetrics[1]?.value).toBe("60.000");
    expect(monthlyMetrics[2]?.value).toBe("57.000");

    expect(allMetrics[1]?.label).toBe("All-Time High");
    expect(allMetrics[2]?.label).toBe("All-Time Low");
    expect(allMetrics[2]?.value).toBe("1.000");
  });

  it("builds observation rows in recency order with movement state", () => {
    const rows = buildObservationRows(buildDatasetDetailFixture().observations, "usd", "$/Gal");
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

  it("formats insight metrics as percentages when metadata unit_type is percent", () => {
    const fixture = buildDatasetDetailFixture();
    const metrics = buildInsightMetrics({
      ...fixture,
      metadata: {
        ...fixture.metadata,
        unit: null,
        unit_type: "percent",
      },
    });

    expect(metrics[0]?.value).toContain("%");
    expect(metrics[1]?.value).toContain("%");
    expect(metrics[2]?.value).toContain("%");
  });
});
