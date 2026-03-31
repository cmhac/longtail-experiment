/** @vitest-environment jsdom */

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  COMPARISON_STATE_EVENT,
  COMPARISON_STATE_STORAGE_KEY,
} from "../src/components/discovery/comparison-state";
import { SiteHeader } from "../src/shell/site-header";

const { navigationState, routerPushMock } = vi.hoisted(() => {
  let searchParams = new URLSearchParams("q=");

  return {
    navigationState: {
      setSearchParams: (nextQuery: string) => {
        searchParams = new URLSearchParams(nextQuery);
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

afterEach(() => {
  document.body.innerHTML = "";
  window.localStorage.clear();
  routerPushMock.mockReset();
  navigationState.setSearchParams("");
});

describe("navbar limited-scope interactions", () => {
  it("keeps Home and Datasets routable while Trends remains disabled", () => {
    render(<SiteHeader />);

    const homeLink = screen.getByTestId("navbar-tab-home");
    const datasetsLink = screen.getByTestId("navbar-tab-datasets");
    const trendsButton = screen.getByTestId("navbar-tab-trends");

    expect(homeLink.getAttribute("href")).toBe("/");
    expect(datasetsLink.getAttribute("href")).toBe("/datasets");
    expect(trendsButton.getAttribute("disabled")).not.toBeNull();
  });

  it("expands search control and closes it on outside click", () => {
    render(<SiteHeader />);

    const searchButton = screen.getByTestId("navbar-search-control");
    expect(screen.queryByTestId("navbar-search-expanded")).toBeNull();

    fireEvent.click(searchButton);
    expect(screen.getByTestId("navbar-search-expanded")).not.toBeNull();

    fireEvent.mouseDown(document.body);
    expect(screen.queryByTestId("navbar-search-expanded")).toBeNull();
  });

  it("submits navbar search to dedicated search route", () => {
    render(<SiteHeader />);

    fireEvent.click(screen.getByTestId("navbar-search-control"));

    const input = screen.getByLabelText("Search datasets");
    fireEvent.change(input, { target: { value: "cpi" } });
    fireEvent.submit(screen.getByTestId("navbar-search-form"));

    expect(routerPushMock).toHaveBeenCalledWith("/search?q=cpi");
  });

  it("routes brand link to homepage", () => {
    render(<SiteHeader />);

    const brandLink = screen.getByTestId("navbar-brand-link");
    expect(brandLink.getAttribute("href")).toBe("/");
  });

  it("shows comparison count and updates on state event", async () => {
    render(<SiteHeader />);

    const comparisonLink = screen.getByTestId("navbar-comparison-link");
    const comparisonCount = screen.getByTestId("navbar-comparison-count");
    expect(comparisonLink.getAttribute("href")).toBe("/comparison");
    expect(comparisonCount.textContent).toBe("0");

    window.localStorage.setItem(
      COMPARISON_STATE_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        selectedDatasetIds: ["A", "B"],
        chartSettings: {
          valueMode: "observed",
          baselineMode: "rolling",
          rollingOffset: 1,
          fixedBaselineDate: null,
        },
        updatedAt: new Date().toISOString(),
      }),
    );
    window.dispatchEvent(new Event(COMPARISON_STATE_EVENT));

    await waitFor(() => {
      expect(screen.getByTestId("navbar-comparison-count").textContent).toBe("2");
    });
  });
});
