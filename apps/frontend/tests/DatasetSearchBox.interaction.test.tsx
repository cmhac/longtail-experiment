/** @vitest-environment jsdom */

import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DatasetSearchBox } from "../src/components/discovery/DatasetSearchBox";

const { navigationState, routerPushMock } = vi.hoisted(() => {
  let searchParams = new URLSearchParams("q=FEDFUNDS");

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

describe("DatasetSearchBox interaction", () => {
  afterEach(() => {
    routerPushMock.mockReset();
    navigationState.setSearchParams("q=FEDFUNDS");
  });

  it("allows typing even when URL query remains unchanged", () => {
    render(<DatasetSearchBox initialQuery="FEDFUNDS" />);

    const input = screen.getByLabelText("Search datasets");
    if (!(input instanceof HTMLInputElement)) {
      throw new Error("Expected search input to be rendered");
    }

    fireEvent.change(input, { target: { value: "FEDFUNDSX" } });

    expect(input.value).toBe("FEDFUNDSX");
  });
});
