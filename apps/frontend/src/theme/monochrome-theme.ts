export type AppearanceMode = "light" | "dark";
export type PreferenceMode = AppearanceMode | "no-preference";

export interface MonochromeModeTokens {
  background: string;
  surface: string;
  border: string;
  foreground: string;
  muted: string;
}

export const MONOCHROME_THEME_TOKENS: Record<AppearanceMode, MonochromeModeTokens> = {
  light: {
    background: "#f5f5f5",
    surface: "#ffffff",
    border: "#d4d4d4",
    foreground: "#111111",
    muted: "#404040",
  },
  dark: {
    background: "#0f0f0f",
    surface: "#171717",
    border: "#3f3f46",
    foreground: "#f5f5f5",
    muted: "#d4d4d8",
  },
};

export const FORBIDDEN_ACCENT_VARIANTS = [
  "primary",
  "secondary",
  "success",
  "warning",
  "danger",
] as const;

export const MONOCHROME_ALLOWED_VARIANTS = ["light", "flat", "bordered"] as const;

export const SHELL_REGION_CLASS_NAMES = {
  header: "shell-region shell-monochrome shell-region-header shell-readable",
  main: "shell-region shell-monochrome shell-region-main shell-readable",
  footer: "shell-region shell-monochrome shell-region-footer shell-readable",
} as const;

export const resolveThemeMode = (preference: PreferenceMode): AppearanceMode => {
  if (preference === "dark") {
    return "dark";
  }

  return "light";
};

export const isMonochromeVariantAllowed = (variant: string): boolean => {
  return !FORBIDDEN_ACCENT_VARIANTS.includes(variant as (typeof FORBIDDEN_ACCENT_VARIANTS)[number]);
};
