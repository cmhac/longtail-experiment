import type { CSSProperties } from "react";

export type ThemePreference = "system" | "light" | "dark";

export interface RootDocumentAttributes {
  dataThemePreference: ThemePreference;
  className: string;
  style: CSSProperties;
}

export const resolveInitialThemePreference = (value?: string): ThemePreference => {
  if (value === "light" || value === "dark") {
    return value;
  }

  return "system";
};

export const createRootDocumentAttributes = (
  preference: ThemePreference = "system",
): RootDocumentAttributes => {
  return {
    dataThemePreference: preference,
    className: "shell-root bg-background text-foreground",
    style: { colorScheme: preference === "system" ? "light dark" : preference },
  };
};
