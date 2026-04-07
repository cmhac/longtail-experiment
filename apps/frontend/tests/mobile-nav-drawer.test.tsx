/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  COMPARISON_STATE_EVENT,
  COMPARISON_STATE_STORAGE_KEY,
} from "../src/components/discovery/comparison-state";
import { SiteHeader } from "../src/shell/site-header";

vi.mock("../src/lib/navigation-client", () => ({
  navigateTo: vi.fn(),
}));

import { navigateTo } from "../src/lib/navigation-client";

const asMock = <T extends (...args: never[]) => unknown>(value: T) => {
  return vi.mocked(value);
};

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams("q="),
}));

let viewportWidth = 390;

const mediaQueryMatches = (query: string, width: number): boolean => {
  const maxWidthMatch = query.match(/max-width:\s*(\d+)px/);
  if (maxWidthMatch && width > Number(maxWidthMatch[1])) {
    return false;
  }

  const minWidthMatch = query.match(/min-width:\s*(\d+)px/);
  if (minWidthMatch && width < Number(minWidthMatch[1])) {
    return false;
  }

  return true;
};

const setViewportWidth = (width: number): void => {
  viewportWidth = width;
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    writable: true,
    value: width,
  });
  window.dispatchEvent(new Event("resize"));
};

const openDrawer = async (): Promise<void> => {
  fireEvent.click(screen.getByTestId("mobile-nav-drawer-trigger"));
  await waitFor(() => {
    expect(screen.getByTestId("mobile-nav-drawer-panel")).not.toBeNull();
  });
};

beforeEach(() => {
  viewportWidth = 390;
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    writable: true,
    value: viewportWidth,
  });
  vi.stubGlobal(
    "matchMedia",
    vi.fn((query: string) => ({
      matches: mediaQueryMatches(query, viewportWidth),
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  );
  asMock(navigateTo).mockReset();
  vi.spyOn(window, "scrollTo").mockImplementation(() => {
    return;
  });
});

afterEach(() => {
  cleanup();
  window.localStorage.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("mobile nav drawer", () => {
  it("opens and closes from trigger and backdrop", async () => {
    const scrollToSpy = vi.mocked(window.scrollTo);
    render(<SiteHeader />);

    await openDrawer();
    expect(document.documentElement.style.overflow).toBe("hidden");
    expect(document.body.style.overflow).toBe("hidden");
    expect(document.body.style.touchAction).toBe("none");

    fireEvent.click(screen.getByTestId("mobile-nav-drawer-backdrop"));

    await waitFor(() => {
      expect(screen.queryByTestId("mobile-nav-drawer-panel")).toBeNull();
    });

    expect(document.documentElement.style.overflow).toBe("");
    expect(document.body.style.overflow).toBe("");
    expect(document.body.style.touchAction).toBe("");
    expect(document.body.style.position).toBe("");
    expect(scrollToSpy).toHaveBeenCalled();
  });

  it("locks body scroll position while open and restores it on close", async () => {
    Object.defineProperty(window, "scrollY", {
      configurable: true,
      writable: true,
      value: 312,
    });
    const scrollToSpy = vi.mocked(window.scrollTo);

    render(<SiteHeader />);

    await openDrawer();
    expect(document.body.style.position).toBe("fixed");
    expect(document.body.style.top).toBe("-312px");
    expect(document.body.style.width).toBe("100%");

    fireEvent.click(screen.getByTestId("mobile-nav-drawer-backdrop"));
    await waitFor(() => {
      expect(screen.queryByTestId("mobile-nav-drawer-panel")).toBeNull();
    });

    expect(scrollToSpy).toHaveBeenCalledWith(0, 312);
  });

  it("renders top-row logo and bell, then required primary row order", async () => {
    render(<SiteHeader />);

    await openDrawer();

    expect(screen.getByTestId("mobile-nav-drawer-brand").textContent).toContain("Longtail");
    expect(screen.getByTestId("mobile-nav-drawer-bell")).not.toBeNull();

    const orderedRows = [
      "mobile-nav-drawer-action-account",
      "mobile-nav-drawer-action-comparison",
      "mobile-nav-drawer-action-search",
      "mobile-nav-drawer-action-home",
      "mobile-nav-drawer-action-sources",
      "mobile-nav-drawer-action-datasets",
    ];

    const primaryActions = screen.getByTestId("mobile-nav-drawer-primary-actions");
    const renderedRows = Array.from(primaryActions.children).map((element) =>
      element.getAttribute("data-testid"),
    );

    expect(renderedRows).toEqual(orderedRows);
  });

  it("closes immediately on destination navigation", async () => {
    render(<SiteHeader />);

    await openDrawer();
    fireEvent.click(screen.getByTestId("mobile-nav-drawer-action-datasets"));

    expect(navigateTo).toHaveBeenCalledWith("/datasets");
    await waitFor(() => {
      expect(screen.queryByTestId("mobile-nav-drawer-panel")).toBeNull();
    });
  });

  it("applies activation threshold at <=1024 and disables above 1024", async () => {
    render(<SiteHeader />);

    await openDrawer();
    setViewportWidth(1025);

    await waitFor(() => {
      expect(screen.queryByTestId("mobile-nav-drawer-panel")).toBeNull();
    });

    fireEvent.click(screen.getByTestId("mobile-nav-drawer-trigger"));
    expect(screen.queryByTestId("mobile-nav-drawer-panel")).toBeNull();

    setViewportWidth(1024);
    await waitFor(() => {
      expect(
        screen.getByTestId("mobile-nav-drawer-trigger").getAttribute("aria-disabled"),
      ).toBeNull();
    });
    await openDrawer();
  });

  it("keeps comparison counter zero-state and mirrors existing comparison count", async () => {
    render(<SiteHeader />);

    await openDrawer();
    expect(screen.getByTestId("mobile-nav-drawer-action-comparison-count").textContent).toBe("0");

    fireEvent.click(screen.getByTestId("mobile-nav-drawer-backdrop"));
    await waitFor(() => {
      expect(screen.queryByTestId("mobile-nav-drawer-panel")).toBeNull();
    });

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

    await openDrawer();
    await waitFor(() => {
      expect(screen.getByTestId("mobile-nav-drawer-action-comparison-count").textContent).toBe("2");
    });
    expect(screen.getByTestId("mobile-nav-drawer-action-comparison-count").textContent).toBe(
      screen.getByTestId("navbar-comparison-count").textContent,
    );
  });

  it("remains stable through repeated open-close interactions and navigation", async () => {
    render(<SiteHeader />);

    for (let cycle = 0; cycle < 4; cycle += 1) {
      await openDrawer();
      fireEvent.click(screen.getByTestId("mobile-nav-drawer-backdrop"));
      await waitFor(() => {
        expect(screen.queryByTestId("mobile-nav-drawer-panel")).toBeNull();
      });
    }

    await openDrawer();
    fireEvent.click(screen.getByTestId("mobile-nav-drawer-action-sources"));
    expect(navigateTo).toHaveBeenCalledWith("/sources");
    await waitFor(() => {
      expect(screen.queryByTestId("mobile-nav-drawer-panel")).toBeNull();
    });
  });
});
