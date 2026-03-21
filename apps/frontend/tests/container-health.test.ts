import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("compose frontend health", () => {
  it("declares frontend with healthcheck", () => {
    const compose = readFileSync(new URL("../../../docker-compose.yml", import.meta.url), "utf8");
    expect(compose).toContain("frontend:");
    expect(compose).toContain("pipeline:");
    expect(compose).toContain("healthcheck:");
  });
});
