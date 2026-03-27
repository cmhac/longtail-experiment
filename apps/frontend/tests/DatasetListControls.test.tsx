/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DatasetListControls } from "../src/components/discovery/DatasetListControls";

void React;

vi.mock("@heroui/react", () => {
  interface MockComboBoxItem {
    value: string;
    label: string;
  }

  interface MockComboBoxProps {
    children: React.ReactNode;
    "data-testid"?: string;
    items?: MockComboBoxItem[];
    onSelectionChange?: (value: string) => void;
    selectedKey?: string;
  }

  const ComboBoxRoot = ({
    items,
    "data-testid": dataTestId,
    onSelectionChange,
    selectedKey,
  }: MockComboBoxProps) => {
    const options = items ?? [];

    return (
      <select
        data-testid={String(dataTestId ?? "dataset-combobox")}
        onChange={(event) => onSelectionChange?.(event.target.value)}
        value={selectedKey ?? ""}
      >
        {options.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>
    );
  };

  const Input = ({ children }: { children?: React.ReactNode }) => <div>{children}</div>;
  const ListBox = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
  const ListBoxItem = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
  const ComboBox = Object.assign(ComboBoxRoot, {
    Root: ComboBoxRoot,
    InputGroup: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    Trigger: ({ children }: { children?: React.ReactNode }) => <div>{children}</div>,
    Popover: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  });

  return {
    ComboBox,
    Input,
    ListBox,
    ListBoxItem,
  };
});

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
  // Regression checklist anchors:
  // - Container surface style parity
  // - Query-param behavior parity for source/category/sort
  // - Left/right control-group layout hooks
  afterEach(() => {
    cleanup();
    navigationState.setSearchParams("");
    routerReplaceMock.mockReset();
  });

  it("renders source, category, and sort controls", () => {
    renderControls();

    expect(screen.getByTestId("dataset-list-controls").className).toContain(
      "dataset-list-controls-surface",
    );
    expect(screen.getByTestId("dataset-filter-left-group")).toBeTruthy();
    expect(screen.getByTestId("dataset-sort-right-group")).toBeTruthy();
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

  it("supports keyboard flow for selection updates", () => {
    renderControls();

    const sourceSelect = screen.getByTestId("dataset-source-filter");
    fireEvent.keyDown(sourceSelect, { key: "ArrowDown" });
    fireEvent.change(sourceSelect, { target: { value: "eia" } });
    fireEvent.keyDown(sourceSelect, { key: "Enter" });

    expect(routerReplaceMock).toHaveBeenCalledWith("/datasets?source=eia");
  });

  it("resets page query param when changing source filter", () => {
    navigationState.setSearchParams("source=eia&page=4");

    render(
      <DatasetListControls
        categoryOptions={[
          { label: "All Categories", value: "all" },
          { label: "energy", value: "energy" },
        ]}
        selectedCategory="all"
        selectedSort="recency"
        selectedSource="eia"
        sourceOptions={[
          { label: "All Sources", value: "all" },
          { label: "EIA", value: "eia" },
          { label: "FRED", value: "fred" },
        ]}
      />,
    );

    fireEvent.change(screen.getByTestId("dataset-source-filter"), {
      target: { value: "fred" },
    });

    expect(routerReplaceMock).toHaveBeenCalledWith("/datasets?source=fred");
  });

  it("resets page query param when changing sort", () => {
    navigationState.setSearchParams("source=eia&page=3");

    render(
      <DatasetListControls
        categoryOptions={[
          { label: "All Categories", value: "all" },
          { label: "energy", value: "energy" },
        ]}
        selectedCategory="all"
        selectedSort="recency"
        selectedSource="eia"
        sourceOptions={[
          { label: "All Sources", value: "all" },
          { label: "EIA", value: "eia" },
        ]}
      />,
    );

    fireEvent.change(screen.getByTestId("dataset-sort-control"), {
      target: { value: "title_asc" },
    });

    expect(routerReplaceMock).toHaveBeenCalledWith("/datasets?source=eia&sort=title_asc");
  });

  it("keeps left and right control group class hooks for layout behavior", () => {
    renderControls();

    expect(screen.getByTestId("dataset-filter-left-group").className).toContain(
      "dataset-list-controls-left-group",
    );
    expect(screen.getByTestId("dataset-sort-right-group").className).toContain(
      "dataset-list-controls-right-group",
    );
  });

  it("keeps responsive layout hook classes for control-row reflow", () => {
    renderControls();

    expect(screen.getByTestId("dataset-list-controls").className).toContain(
      "dataset-list-controls",
    );
    expect(screen.getByTestId("dataset-filter-left-group").className).toContain(
      "dataset-list-controls-left-group",
    );
    expect(screen.getByTestId("dataset-sort-right-group").className).toContain(
      "dataset-list-controls-right-group",
    );
  });
});
