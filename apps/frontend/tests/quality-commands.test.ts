import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("frontend quality command contracts", () => {
  it("defines lint, format, typecheck, test, and coverage scripts", () => {
    const packageJson = JSON.parse(
      readFileSync(new URL("../package.json", import.meta.url), "utf8"),
    ) as {
      scripts: Record<string, string>;
    };

    expect(packageJson.scripts.lint).toBeTruthy();
    expect(packageJson.scripts.format).toBeTruthy();
    expect(packageJson.scripts.typecheck).toBeTruthy();
    expect(packageJson.scripts.test).toBeTruthy();
    expect(packageJson.scripts.coverage).toBeTruthy();
  });

  it("documents quickstart quality command flow", () => {
    const quickstart = readFileSync(
      new URL("../../../specs/015-scaffold-page-furniture/quickstart.md", import.meta.url),
      "utf8",
    );

    expect(quickstart).toContain("pnpm --dir apps/frontend lint");
    expect(quickstart).toContain("pnpm --dir apps/frontend typecheck");
    expect(quickstart).toContain("pnpm --dir apps/frontend coverage");
    expect(quickstart).toContain("pnpm run affected:test");
  });

  it("documents local startup command", () => {
    const quickstart = readFileSync(
      new URL("../../../specs/015-scaffold-page-furniture/quickstart.md", import.meta.url),
      "utf8",
    );

    expect(quickstart).toContain("pnpm --dir apps/frontend dev");
  });
});
