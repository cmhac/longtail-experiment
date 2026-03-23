import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  MONOCHROME_THEME_TOKENS,
  SHELL_REGION_CLASS_NAMES,
  resolveThemeMode,
} from "../src/theme/monochrome-theme";
import {
  createRootDocumentAttributes,
  resolveInitialThemePreference,
} from "../src/theme/theme-preference";

describe("shell theme preference contracts", () => {
  it("asserts light preference resolves to light shell mode", () => {
    expect(resolveThemeMode("light")).toBe("light");
    expect(resolveInitialThemePreference("light")).toBe("light");
    expect(MONOCHROME_THEME_TOKENS.light.foreground).toBe("#111111");
  });

  it("asserts dark preference resolves to dark shell mode", () => {
    expect(resolveThemeMode("dark")).toBe("dark");
    expect(resolveInitialThemePreference("dark")).toBe("dark");
    expect(MONOCHROME_THEME_TOKENS.dark.foreground).toBe("#f5f5f5");
  });

  it("asserts readability class contracts are present for both modes", () => {
    expect(SHELL_REGION_CLASS_NAMES.header).toContain("shell-readable");
    expect(SHELL_REGION_CLASS_NAMES.main).toContain("shell-readable");
    expect(SHELL_REGION_CLASS_NAMES.footer).toContain("shell-readable");
  });

  it("regresses preference switching between sessions", () => {
    const firstSession = resolveThemeMode("light");
    const secondSession = resolveThemeMode("dark");
    const systemSession = createRootDocumentAttributes(resolveInitialThemePreference());

    expect(firstSession).toBe("light");
    expect(secondSession).toBe("dark");
    expect(systemSession.style.colorScheme).toBe("light dark");
  });

  it("documents device preference media query tokens in globals", () => {
    const globalsCss = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");

    expect(globalsCss).toContain("@media (prefers-color-scheme: dark)");
    expect(globalsCss).toContain("--shell-foreground");
  });
});
