/** @vitest-environment jsdom */

import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { InfiniteSearchResults } from "../src/components/discovery/InfiniteSearchResults";

const observers: Array<(entries: Array<{ isIntersecting: boolean }>) => void> = [];

beforeEach(() => {
  observers.length = 0;

  class MockIntersectionObserver {
    private readonly callback: (entries: Array<{ isIntersecting: boolean }>) => void;

    constructor(callback: (entries: Array<{ isIntersecting: boolean }>) => void) {
      this.callback = callback;
      observers.push(this.callback);
    }

    observe(): void {}
    disconnect(): void {}
    unobserve(): void {}
  }

  vi.stubGlobal("IntersectionObserver", MockIntersectionObserver);
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("InfiniteSearchResults", () => {
  it("requests search page 2 when sentinel intersects", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        items: [
          {
            dataset_id: "PAGE2",
            source: { id: "fred", name: "FRED" },
            title: "Search Page 2 Dataset",
            description: null,
            geographic_scope: "US",
            topic_tags: [],
            latest_update_at: "2026-03-01T00:00:00Z",
          },
        ],
        page: 2,
        total_pages: 2,
      }),
    } as Response);

    render(
      <InfiniteSearchResults
        initialItems={[
          {
            dataset_id: "PAGE1",
            source: { id: "fred", name: "FRED" },
            title: "Search Page 1 Dataset",
            description: null,
            geographic_scope: "US",
            topic_tags: [],
            latest_update_at: "2026-03-01T00:00:00Z",
          },
        ]}
        initialPage={1}
        initialTotalPages={2}
        query="inflation"
      />,
    );

    expect(screen.getByTestId("infinite-search-sentinel")).toBeTruthy();

    const observerCallback = observers[0];
    if (!observerCallback) {
      throw new Error("Expected observer callback to be registered");
    }

    observerCallback([{ isIntersecting: true }]);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/discovery/datasets/search?q=inflation&page=2",
        expect.objectContaining({ method: "GET" }),
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Search Page 2 Dataset")).toBeTruthy();
    });
  });
});
