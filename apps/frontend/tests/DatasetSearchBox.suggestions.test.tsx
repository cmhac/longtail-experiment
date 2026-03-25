/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DatasetSearchBox } from "../src/components/discovery/DatasetSearchBox";
import * as discoveryClient from "../src/lib/api/discovery-client";

const { routerPushMock, navigationState } = vi.hoisted(() => {
  let searchParams = new URLSearchParams();

  return {
    navigationState: {
      setSearchParams: (query: string) => {
        searchParams = new URLSearchParams(query);
      },
      getSearchParams: () => searchParams,
    },
    routerPushMock: vi.fn(),
  };
});

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: routerPushMock }),
  useSearchParams: () => navigationState.getSearchParams(),
}));

describe("DatasetSearchBox suggestions", () => {
  afterEach(() => {
    cleanup();
    navigationState.setSearchParams("");
    vi.restoreAllMocks();
    routerPushMock.mockReset();
  });

  it("shows likely suggestions while typing and navigates on selection", async () => {
    vi.spyOn(discoveryClient, "fetchSearchSuggestions").mockResolvedValue({
      query: "fund",
      limit: 5,
      items: [
        {
          dataset_id: "FEDFUNDS",
          source: { id: "fred", name: "FRED" },
          title: "Federal Funds Effective Rate",
          rank_score: 0.91,
        },
      ],
    });

    render(<DatasetSearchBox initialQuery="" summary={null} />);

    const input = screen.getByPlaceholderText("Search datasets");
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: "fund" } });

    await waitFor(() => {
      expect(screen.queryByTestId("dataset-search-suggestions")).not.toBeNull();
    });

    const suggestions = screen.getByTestId("dataset-search-suggestions");
    Object.defineProperty(suggestions, "scrollHeight", { configurable: true, value: 400 });
    Object.defineProperty(suggestions, "clientHeight", { configurable: true, value: 200 });
    Object.defineProperty(suggestions, "scrollTop", {
      configurable: true,
      value: 0,
      writable: true,
    });
    fireEvent.wheel(suggestions, { deltaY: -18 });

    expect(screen.getByText("SEARCH RESULTS (1)")).toBeDefined();
    expect(screen.getByText("Press ↵ to view all")).toBeDefined();
    expect(screen.getByText("DATASET • FRED")).toBeDefined();

    fireEvent.mouseDown(screen.getByTestId("dataset-search-suggestion-item"));
    fireEvent.click(screen.getByTestId("dataset-search-suggestion-item"));

    expect(routerPushMock).toHaveBeenCalledWith("/datasets/FEDFUNDS");
  });

  it("clears stale suggestions when latest request returns no matches", async () => {
    const fetchSpy = vi.spyOn(discoveryClient, "fetchSearchSuggestions");
    fetchSpy.mockResolvedValueOnce({
      query: "fund",
      limit: 5,
      items: [
        {
          dataset_id: "FEDFUNDS",
          source: { id: "fred", name: "FRED" },
          title: "Federal Funds Effective Rate",
          rank_score: 0.91,
        },
      ],
    });
    fetchSpy.mockResolvedValueOnce({
      query: "zzzzz",
      limit: 5,
      items: [],
    });

    render(<DatasetSearchBox initialQuery="" summary={null} />);

    const input = screen.getByPlaceholderText("Search datasets");
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: "fund" } });

    await waitFor(() => {
      expect(screen.queryByTestId("dataset-search-suggestions")).not.toBeNull();
    });

    fireEvent.change(input, { target: { value: "zzzzz" } });

    await waitFor(() => {
      expect(screen.queryByTestId("dataset-search-suggestions")).toBeNull();
    });
  });
});
