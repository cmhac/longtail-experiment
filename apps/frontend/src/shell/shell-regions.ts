export const SHELL_REGION_KEYS = ["header", "main-placeholder", "footer"] as const;

export type ShellRegionKey = (typeof SHELL_REGION_KEYS)[number];

export interface ShellRegionDefinition {
  key: ShellRegionKey;
  order: number;
  testId: string;
  landmarkRole: "banner" | "main" | "contentinfo";
}

export const SHELL_REGIONS: readonly ShellRegionDefinition[] = [
  { key: "header", order: 1, testId: "shell-header", landmarkRole: "banner" },
  { key: "main-placeholder", order: 2, testId: "shell-main-placeholder", landmarkRole: "main" },
  { key: "footer", order: 3, testId: "shell-footer", landmarkRole: "contentinfo" },
] as const;

export const SHELL_REGION_ORDER = SHELL_REGIONS.map((region) => region.key);
