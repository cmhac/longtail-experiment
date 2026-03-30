/** @vitest-environment jsdom */

import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { InfiniteCatalogList } from "../src/components/discovery/InfiniteCatalogList";

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

describe("InfiniteCatalogList", () => {
  it("requests the next page when sentinel intersects", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        items: [
          {
            dataset_id: "PAGE2",
            source: { id: "fred", name: "FRED" },
            title: "Page 2 Dataset",
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
      <InfiniteCatalogList
        emptyMessage="No data"
        initialItems={[
          {
            dataset_id: "PAGE1",
            source: { id: "fred", name: "FRED" },
            title: "Page 1 Dataset",
            description: null,
            geographic_scope: "US",
            topic_tags: [],
            latest_update_at: "2026-03-01T00:00:00Z",
          },
        ]}
        initialPage={1}
        initialTotalPages={2}
        requestPath="/api/discovery/datasets"
        requestQuery={{ sort: "recency" }}
      />,
    );

    expect(screen.getByTestId("discovery-feed-list-wrapper")).toBeTruthy();
    expect(screen.getByTestId("infinite-scroll-sentinel")).toBeTruthy();

    const observerCallback = observers[0];
    if (!observerCallback) {
      throw new Error("Expected observer callback to be registered");
    }

    observerCallback([{ isIntersecting: true }]);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/discovery/datasets?sort=recency&page=2",
        expect.objectContaining({ method: "GET" }),
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Page 2 Dataset")).toBeTruthy();
    });

    expect(screen.getByTestId("discovery-feed-list-wrapper")).toBeTruthy();
  });

  it("resets rendered rows when request query changes", async () => {
    const { rerender } = render(
      <InfiniteCatalogList
        emptyMessage="No data"
        initialItems={[
          {
            dataset_id: "EIA.OLD",
            source: { id: "eia", name: "EIA" },
            title: "Old Filter Row",
            description: null,
            geographic_scope: "US",
            topic_tags: [],
            latest_update_at: "2026-03-01T00:00:00Z",
          },
        ]}
        initialPage={1}
        initialTotalPages={1}
        requestPath="/api/discovery/datasets"
        requestQuery={{ source: "eia" }}
      />,
    );

    expect(screen.getByText("Old Filter Row")).toBeTruthy();

    rerender(
      <InfiniteCatalogList
        emptyMessage="No data"
        initialItems={[
          {
            dataset_id: "BLS.NEW",
            source: { id: "bls", name: "BLS" },
            title: "New Filter Row",
            description: null,
            geographic_scope: "US",
            topic_tags: [],
            latest_update_at: "2026-03-01T00:00:00Z",
          },
        ]}
        initialPage={1}
        initialTotalPages={1}
        requestPath="/api/discovery/datasets"
        requestQuery={{ source: "bls" }}
      />,
    );

    await waitFor(() => {
      expect(screen.queryByText("Old Filter Row")).toBeNull();
      expect(screen.getByText("New Filter Row")).toBeTruthy();
    });
  });
});
