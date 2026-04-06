export type NavbarTabKey = "home" | "sources" | "datasets";

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

export const MOBILE_DRAWER_MAX_WIDTH_PX = 1024;
export const MOBILE_DRAWER_MEDIA_QUERY = `(max-width: ${MOBILE_DRAWER_MAX_WIDTH_PX}px)`;

export const isMobileDrawerViewportWidth = (width: number): boolean => {
  return width <= MOBILE_DRAWER_MAX_WIDTH_PX;
};

export type MobileDrawerPrimaryItemKey =
  | "account"
  | "comparison"
  | "search"
  | "home"
  | "sources"
  | "datasets";

export interface MobileDrawerPrimaryItemConfig {
  key: MobileDrawerPrimaryItemKey;
  label: string;
  destination: string;
  isProtected: boolean;
  orderIndex: number;
}

export type MobileDrawerFooterItemKey = "admin" | "sign_out";

export interface MobileDrawerFooterItemConfig {
  key: MobileDrawerFooterItemKey;
  label: string;
  destination: string;
  isProtected: boolean;
  orderIndex: number;
}

const BASE_NAVBAR_TABS: readonly Omit<NavbarTabConfig, "isActive">[] = [
  {
    key: "home",
    label: "Home",
    href: "/",
    isEnabled: true,
  },
  {
    key: "sources",
    label: "Sources",
    href: "/sources",
    isEnabled: true,
  },
  {
    key: "datasets",
    label: "Datasets",
    href: "/datasets",
    isEnabled: true,
  },
] as const;

export const resolveNavbarTabs = (activeTab: NavbarTabKey): readonly NavbarTabConfig[] => {
  return BASE_NAVBAR_TABS.map((tab) => ({
    ...tab,
    isActive: tab.key === activeTab,
  }));
};

export const MOBILE_DRAWER_PRIMARY_ITEMS: readonly MobileDrawerPrimaryItemConfig[] = [
  {
    key: "account",
    label: "Account",
    destination: "/settings",
    isProtected: true,
    orderIndex: 1,
  },
  {
    key: "comparison",
    label: "Comparison",
    destination: "/comparison",
    isProtected: true,
    orderIndex: 2,
  },
  {
    key: "search",
    label: "Search",
    destination: "/search",
    isProtected: false,
    orderIndex: 3,
  },
  {
    key: "home",
    label: "Home",
    destination: "/",
    isProtected: false,
    orderIndex: 4,
  },
  {
    key: "sources",
    label: "Sources",
    destination: "/sources",
    isProtected: false,
    orderIndex: 5,
  },
  {
    key: "datasets",
    label: "Datasets",
    destination: "/datasets",
    isProtected: false,
    orderIndex: 6,
  },
] as const;

export const MOBILE_DRAWER_FOOTER_ITEMS: readonly MobileDrawerFooterItemConfig[] = [
  {
    key: "admin",
    label: "Admin",
    destination: "/admin",
    isProtected: true,
    orderIndex: 1,
  },
  {
    key: "sign_out",
    label: "Sign out",
    destination: "/",
    isProtected: false,
    orderIndex: 2,
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
