import React from "react";
import { describe, expect, it, vi } from "vitest";
import ComparisonPage from "../src/app/comparison/page";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("comparison page", () => {
  it("renders comparison shell and auth-redirect fallback", () => {
    const markup = renderMarkup(<ComparisonPage />);

    expect(markup).toContain('data-testid="comparison-page"');
    expect(markup).toContain('data-testid="comparison-auth-redirecting"');
    expect(markup).toContain('data-testid="navbar-comparison-link"');
  });
});
