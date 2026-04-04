import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { SHELL_REGION_CLASS_NAMES } from "../src/theme/monochrome-theme";

describe("shell theme preference contracts", () => {
  it("asserts shell region class contracts no longer depend on monochrome helpers", () => {
    expect(SHELL_REGION_CLASS_NAMES.header).not.toContain("shell-monochrome");
    expect(SHELL_REGION_CLASS_NAMES.main).not.toContain("shell-monochrome");
    expect(SHELL_REGION_CLASS_NAMES.footer).not.toContain("shell-monochrome");
    expect(SHELL_REGION_CLASS_NAMES.header).not.toContain("shell-readable");
    expect(SHELL_REGION_CLASS_NAMES.main).not.toContain("shell-readable");
    expect(SHELL_REGION_CLASS_NAMES.footer).not.toContain("shell-readable");
  });

  it("documents HeroUI-driven globals without legacy theme-preference selectors", () => {
    const globalsCss = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");

    expect(globalsCss).not.toContain("data-theme-preference");
  });
});
