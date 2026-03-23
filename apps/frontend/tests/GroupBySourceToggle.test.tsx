import React from "react";
import { describe, expect, it, vi } from "vitest";
import {
  GroupBySourceToggle,
  buildGroupToggleUrl,
} from "../src/components/discovery/GroupBySourceToggle";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/datasets",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams("group=source"),
}));

describe("GroupBySourceToggle", () => {
  it("renders toggle with grouped state from URL param", () => {
    const markup = renderMarkup(<GroupBySourceToggle />);

    expect(markup).toContain('data-testid="group-by-source-toggle"');
    expect(markup).toContain('aria-pressed="true"');
    expect(markup).toContain("Group by source");
  });

  it("builds enabled and disabled toggle URLs", () => {
    expect(buildGroupToggleUrl("/datasets", new URLSearchParams())).toBe("/datasets?group=source");
    expect(buildGroupToggleUrl("/datasets", new URLSearchParams("group=source"))).toBe("/datasets");
  });
});
