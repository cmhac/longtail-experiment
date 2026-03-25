import React from "react";
import { describe, expect, it, vi } from "vitest";
import { DatasetSearchBox, buildSearchUrl } from "../src/components/discovery/DatasetSearchBox";
import { renderMarkup } from "./test-utils";

const routerPushMock = () => undefined;

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: routerPushMock }),
  useSearchParams: () => new URLSearchParams("q=federal"),
}));

describe("DatasetSearchBox", () => {
  it("renders search input with placeholder and no submit button", () => {
    const markup = renderMarkup(<DatasetSearchBox />);

    expect(markup).toContain('placeholder="Search datasets"');
    expect(markup).toContain('type="text"');
    expect(markup).not.toContain('type="submit"');
  });

  it("pre-populates input value from initial query", () => {
    const markup = renderMarkup(<DatasetSearchBox initialQuery="federal" />);

    expect(markup).toContain('value="federal"');
  });

  it("builds URL with query and strips blank search text", () => {
    expect(buildSearchUrl("/datasets", "interest rates")).toBe("/datasets?q=interest+rates");
    expect(buildSearchUrl("/datasets", "   ")).toBe("/datasets");
  });
});
