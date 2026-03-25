/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DatasetListControls } from "../src/components/discovery/DatasetListControls";

const { navigationState, routerReplaceMock } = vi.hoisted(() => {
  let searchParams = new URLSearchParams();

  return {
    navigationState: {
      setSearchParams: (query: string) => {
        searchParams = new URLSearchParams(query);
      },
      getSearchParams: () => searchParams,
    },
    routerReplaceMock: vi.fn(),
  };
});

vi.mock("next/navigation", () => ({
  usePathname: () => "/datasets",
  useRouter: () => ({ replace: routerReplaceMock }),
  useSearchParams: () => navigationState.getSearchParams(),
}));

const renderControls = (): void => {
  render(
    <DatasetListControls
      categoryOptions={[
        { label: "All Categories", value: "all" },
        { label: "energy", value: "energy" },
      ]}
      selectedCategory="all"
      selectedSort="recency"
      selectedSource="all"
      sourceOptions={[
        { label: "All Sources", value: "all" },
        { label: "EIA", value: "eia" },
      ]}
    />,
  );
};

describe("DatasetListControls", () => {
  afterEach(() => {
    cleanup();
    navigationState.setSearchParams("");
    routerReplaceMock.mockReset();
  });

  it("renders source, category, and sort controls", () => {
    renderControls();

    expect(screen.getByTestId("dataset-source-filter")).toBeTruthy();
    expect(screen.getByTestId("dataset-category-filter")).toBeTruthy();
    expect(screen.getByTestId("dataset-sort-control")).toBeTruthy();
  });

  it("updates source filter query param on selection", () => {
    renderControls();

    const sourceSelect = screen.getByTestId("dataset-source-filter");
    fireEvent.change(sourceSelect, { target: { value: "eia" } });

    expect(routerReplaceMock).toHaveBeenCalledWith("/datasets?source=eia");
  });

  it("updates category filter query param on selection", () => {
    renderControls();

    const categorySelect = screen.getByTestId("dataset-category-filter");
    fireEvent.change(categorySelect, { target: { value: "energy" } });

    expect(routerReplaceMock).toHaveBeenCalledWith("/datasets?category=energy");
  });

  it("removes query param when source is reset to default option", () => {
    navigationState.setSearchParams("source=eia&sort=title_asc");

    render(
      <DatasetListControls
        categoryOptions={[
          { label: "All Categories", value: "all" },
          { label: "energy", value: "energy" },
        ]}
        selectedCategory="all"
        selectedSort="title_asc"
        selectedSource="eia"
        sourceOptions={[
          { label: "All Sources", value: "all" },
          { label: "EIA", value: "eia" },
        ]}
      />,
    );

    const sourceSelect = screen.getByTestId("dataset-source-filter");
    fireEvent.change(sourceSelect, { target: { value: "all" } });

    expect(routerReplaceMock).toHaveBeenCalledWith("/datasets?sort=title_asc");
  });

  it("sets title_desc sort mode in URL", () => {
    renderControls();

    const sortSelect = screen.getByTestId("dataset-sort-control");
    fireEvent.change(sortSelect, { target: { value: "title_desc" } });

    expect(routerReplaceMock).toHaveBeenCalledWith("/datasets?sort=title_desc");
  });
});
