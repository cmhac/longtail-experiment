export type NavbarTabKey = "home" | "datasets" | "trends";

export interface NavbarTabConfig {
  key: NavbarTabKey;
  label: string;
  href?: string;
  isEnabled: boolean;
  isActive: boolean;
}

export type NavbarUtilityKey = "search" | "profile";

export interface NavbarUtilityControlConfig {
  key: NavbarUtilityKey;
  label: string;
  isEnabled: boolean;
}

export const NAVBAR_TABS: readonly NavbarTabConfig[] = [
  {
    key: "home",
    label: "Home",
    href: "/",
    isEnabled: true,
    isActive: true,
  },
  {
    key: "datasets",
    label: "Datasets",
    isEnabled: false,
    isActive: false,
  },
  {
    key: "trends",
    label: "Trends",
    isEnabled: false,
    isActive: false,
  },
] as const;

export const NAVBAR_UTILITY_CONTROLS: readonly NavbarUtilityControlConfig[] = [
  {
    key: "search",
    label: "Search",
    isEnabled: false,
  },
  {
    key: "profile",
    label: "Profile",
    isEnabled: true,
  },
] as const;
