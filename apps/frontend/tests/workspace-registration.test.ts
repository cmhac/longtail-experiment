import { existsSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("workspace registration", () => {
  it("has frontend project config", () => {
    expect(existsSync(new URL("../project.json", import.meta.url))).toBe(true);
  });
});
