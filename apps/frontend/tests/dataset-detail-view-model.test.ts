import { describe, expect, it } from "vitest";
import {
  DEFAULT_RELATIVE_CHANGE_SETTINGS,
  buildInsightMetrics,
  buildObservationRows,
  computeRelativeChangePercent,
  filterObservationRange,
  formatObservedOn,
  formatValue,
  getAvailableTrendRanges,
  getMetadataRows,
  projectRelativeChangeGaps,
  projectRelativeChangeSeries,
  toRollingBaselineIndex,
} from "../src/components/discovery/dataset-detail-view-model";
import {
  buildDatasetDetailFixture,
  buildLongHistoryDatasetDetailFixture,
  buildObservationHistory,
  buildZeroBaselineFixture,
} from "./fixtures/dataset-detail-fixtures";

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
    expect(high.label).toBe("All-Time High");
    expect(low.label).toBe("All-Time Low");
  });

  it("uses selected chart range to set high/low labels and values", () => {
    const fixture = buildDatasetDetailFixture();
    const manyObservations = buildObservationHistory({
      count: 60,
      start: "2023-01-01",
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
    expect(monthlyMetrics[2]?.value).toBe("56.000");

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
    const observations = buildLongHistoryDatasetDetailFixture().observations;

    expect(filterObservationRange(observations, "1M").length).toBeLessThan(observations.length);
    expect(filterObservationRange(observations, "5Y").length).toBeLessThan(observations.length);
    expect(filterObservationRange(observations, "ALL")).toHaveLength(observations.length);
  });

  it("returns available trend ranges ordered from longest to shortest", () => {
    expect(getAvailableTrendRanges(buildLongHistoryDatasetDetailFixture().observations)).toEqual([
      "ALL",
      "5Y",
      "1Y",
      "6M",
      "1M",
    ]);
  });

  it("hides unsupported trend ranges for limited histories", () => {
    const observations = buildDatasetDetailFixture().observations;

    expect(getAvailableTrendRanges(observations)).toEqual(["ALL"]);
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

  it("computes signed baseline-relative change percentages", () => {
    expect(computeRelativeChangePercent(120, 100)).toBe(20);
    expect(computeRelativeChangePercent(80, 100)).toBe(-20);
    expect(computeRelativeChangePercent(100, 100)).toBe(0);
    expect(computeRelativeChangePercent(10, 0)).toBeNull();
  });

  it("computes rolling baseline indexes", () => {
    expect(toRollingBaselineIndex(4, 1)).toBe(3);
    expect(toRollingBaselineIndex(4, 3)).toBe(1);
    expect(toRollingBaselineIndex(2, 3)).toBe(-1);
  });

  it("projects rolling relative-change points with gap semantics", () => {
    const fixture = buildDatasetDetailFixture({
      observations: [
        {
          observed_on: "2024-01-01",
          value: 100,
          reported_at: "2024-01-01T00:00:00Z",
          attributes: {},
        },
        {
          observed_on: "2024-01-02",
          value: 110,
          reported_at: "2024-01-02T00:00:00Z",
          attributes: {},
        },
        {
          observed_on: "2024-01-03",
          value: 99,
          reported_at: "2024-01-03T00:00:00Z",
          attributes: {},
        },
      ],
    });

    const projection = projectRelativeChangeSeries(fixture.observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "rolling",
      rollingOffset: 1,
      valueMode: "relative",
    });

    expect(projection.points[0]?.computability).toBe("insufficient-history");
    expect(projection.points[1]?.value).toBe(10);
    expect(projection.points[2]?.value).toBeCloseTo(-10);
    expect(projection.hasComputablePoints).toBe(true);
  });

  it("supports rolling offsets 1, 2, 3 and n", () => {
    const fixture = buildDatasetDetailFixture({
      observations: buildObservationHistory({
        count: 8,
        initialValue: 100,
        start: "2024-01-01",
        valueStep: 10,
      }),
    });

    const offsetOne = projectRelativeChangeSeries(fixture.observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "rolling",
      rollingOffset: 1,
      valueMode: "relative",
    });
    const offsetThree = projectRelativeChangeSeries(fixture.observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "rolling",
      rollingOffset: 3,
      valueMode: "relative",
    });
    const offsetN = projectRelativeChangeSeries(fixture.observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "rolling",
      rollingOffset: 5,
      valueMode: "relative",
    });

    expect(offsetOne.points.filter((point) => point.value !== null).length).toBe(7);
    expect(offsetThree.points.filter((point) => point.value !== null).length).toBe(5);
    expect(offsetN.points.filter((point) => point.value !== null).length).toBe(3);
  });

  it("supports fixed baselines by exact date", () => {
    const fixture = buildDatasetDetailFixture({
      observations: [
        {
          observed_on: "2024-01-01",
          value: 100,
          reported_at: "2024-01-01T00:00:00Z",
          attributes: {},
        },
        {
          observed_on: "2024-01-02",
          value: 120,
          reported_at: "2024-01-02T00:00:00Z",
          attributes: {},
        },
        {
          observed_on: "2024-01-03",
          value: 140,
          reported_at: "2024-01-03T00:00:00Z",
          attributes: {},
        },
      ],
    });

    const projection = projectRelativeChangeSeries(fixture.observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "fixed",
      fixedBaselineDate: "2024-01-02",
      fixedSelectionMode: "date",
      valueMode: "relative",
    });

    expect(projection.points[0]?.computability).toBe("before-fixed-baseline");
    expect(projection.points[1]?.value).toBe(0);
    expect(projection.points[2]?.value).toBeCloseTo(16.6666667);
  });

  it("supports fixed baselines by index/offset", () => {
    const fixture = buildDatasetDetailFixture({
      observations: buildObservationHistory({
        count: 5,
        initialValue: 100,
        start: "2024-01-01",
        valueStep: 5,
      }),
    });

    const projection = projectRelativeChangeSeries(fixture.observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "fixed",
      fixedBaselineOffset: 2,
      fixedSelectionMode: "offset",
      valueMode: "relative",
    });

    expect(projection.points[0]?.computability).toBe("before-fixed-baseline");
    expect(projection.points[1]?.computability).toBe("before-fixed-baseline");
    expect(projection.points[2]?.value).toBe(0);
    expect(projection.points[4]?.value).toBeCloseTo(9.0909091);
  });

  it("returns missing-baseline when fixed date is not available", () => {
    const projection = projectRelativeChangeSeries(buildDatasetDetailFixture().observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "fixed",
      fixedBaselineDate: "2024-02-01",
      fixedSelectionMode: "date",
      valueMode: "relative",
    });

    expect(projection.points.every((point) => point.value === null)).toBe(true);
    expect(projection.points.every((point) => point.computability === "missing-baseline")).toBe(
      true,
    );
  });

  it("projects non-computable points as timeline gaps", () => {
    const projection = projectRelativeChangeSeries(buildDatasetDetailFixture().observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "rolling",
      rollingOffset: 4,
      valueMode: "relative",
    });

    const gapSeries = projectRelativeChangeGaps(projection.points);
    expect(gapSeries).toHaveLength(buildDatasetDetailFixture().observations.length);
    expect(gapSeries.every((point) => point.value === null)).toBe(true);
  });

  it("builds relative insight metrics in percent mode", () => {
    const metrics = buildInsightMetrics(buildDatasetDetailFixture(), "ALL", {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "rolling",
      rollingOffset: 1,
      valueMode: "relative",
    });

    expect(metrics[0]?.value).toContain("%");
    expect(metrics[1]?.value).toContain("%");
    expect(metrics[2]?.value).toContain("%");
  });

  it("returns no-computable relative insight fallback when baseline is unavailable", () => {
    const metrics = buildInsightMetrics(buildDatasetDetailFixture(), "ALL", {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "fixed",
      fixedBaselineDate: null,
      fixedSelectionMode: "date",
      valueMode: "relative",
    });

    expect(metrics[0]?.value).toBe("No computable relative points");
    expect(metrics[1]?.value).toBe("--");
    expect(metrics[2]?.value).toBe("--");
  });

  it("marks zero-baseline points as non-computable", () => {
    const projection = projectRelativeChangeSeries(buildZeroBaselineFixture().observations, {
      ...DEFAULT_RELATIVE_CHANGE_SETTINGS,
      baselineMode: "rolling",
      rollingOffset: 1,
      valueMode: "relative",
    });

    expect(projection.points[1]?.computability).toBe("zero-baseline");
    expect(projection.points[1]?.value).toBeNull();
  });
});
