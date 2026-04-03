/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DatasetSearchBox } from "../src/components/discovery/DatasetSearchBox";

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
  cleanup();
  routerPushMock.mockReset();
  navigationState.setSearchParams("");
  document.body.innerHTML = "";
});

describe("unified search surface contract", () => {
  it("routes homepage submit to dedicated search page", () => {
    navigationState.setSearchParams("q=inflation");
    render(<DatasetSearchBox initialQuery="inflation" submitPath="/search" />);

    fireEvent.submit(screen.getByTestId("dataset-search-form"));

    expect(routerPushMock).toHaveBeenCalledWith("/search?q=inflation");
  });

  it("does not navigate for whitespace-only submissions", () => {
    render(<DatasetSearchBox initialQuery="inflation" submitPath="/search" />);

    const input = screen.getByLabelText("Search datasets");
    fireEvent.change(input, { target: { value: "   " } });
    fireEvent.submit(screen.getByTestId("dataset-search-form"));

    expect(routerPushMock).not.toHaveBeenCalled();
  });
});
