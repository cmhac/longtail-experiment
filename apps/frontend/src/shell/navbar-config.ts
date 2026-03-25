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

const BASE_NAVBAR_TABS: readonly Omit<NavbarTabConfig, "isActive">[] = [
  {
    key: "home",
    label: "Home",
    href: "/",
    isEnabled: true,
  },
  {
    key: "datasets",
    label: "Datasets",
    href: "/datasets",
    isEnabled: true,
  },
  {
    key: "trends",
    label: "Trends",
    isEnabled: false,
  },
] as const;

export const resolveNavbarTabs = (activeTab: NavbarTabKey): readonly NavbarTabConfig[] => {
  return BASE_NAVBAR_TABS.map((tab) => ({
    ...tab,
    isActive: tab.key === activeTab,
  }));
};

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
