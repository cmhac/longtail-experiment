import { describe, expect, it } from "vitest";

import { TREND_DIRECTION_TOKENS } from "../../src/components/trends/trendDirectionTokens";

describe("TrendDirectionAccessibility", () => {
  it("provides dual direction encoding metadata", () => {
    expect(TREND_DIRECTION_TOKENS.up.ariaLabel).toContain("Upward");
    expect(TREND_DIRECTION_TOKENS.up.icon).not.toBe(TREND_DIRECTION_TOKENS.down.icon);
    expect(TREND_DIRECTION_TOKENS.up.overlayClassName).not.toBe(
      TREND_DIRECTION_TOKENS.down.overlayClassName,
    );
  });
});
