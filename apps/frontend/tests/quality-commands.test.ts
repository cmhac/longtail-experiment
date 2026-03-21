import { existsSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("frontend quality files", () => {
  it("has tsconfig and vitest config", () => {
    expect(existsSync(new URL("../tsconfig.json", import.meta.url))).toBe(true);
    expect(existsSync(new URL("../vitest.config.ts", import.meta.url))).toBe(true);
  });
});
