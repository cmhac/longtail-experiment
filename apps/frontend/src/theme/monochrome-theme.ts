export const SHELL_LAYOUT_CLASS_NAMES = {
  page: "shell-page shell-scroll-anchor",
  constrainedContent: "shell-content-constrained",
  explicitFullWidth: "shell-region-full-width",
} as const;

export const SHELL_REGION_CLASS_NAMES = {
  header: "shell-region shell-region-header shell-region-full-width",
  main: "shell-region shell-region-main",
  footer: "shell-region shell-region-footer shell-region-full-width",
} as const;

export const SHELL_NAVBAR_CLASS_NAMES = {
  card: "shell-navbar-card",
  nav: "shell-navbar",
  brandRegion: "shell-navbar-brand-region",
  brandLink: "shell-navbar-brand-link",
  mobileDrawerTrigger: "shell-navbar-mobile-drawer-trigger",
  mobileDrawerRoot: "shell-mobile-drawer-root",
  mobileDrawerBackdrop: "shell-mobile-drawer-backdrop",
  mobileDrawerPanel: "shell-mobile-drawer-panel",
  mobileDrawerHeader: "shell-mobile-drawer-header",
  mobileDrawerHeaderBrand: "shell-mobile-drawer-header-brand",
  mobileDrawerPrimary: "shell-mobile-drawer-primary",
  mobileDrawerFooter: "shell-mobile-drawer-footer",
  mobileDrawerActionRow: "shell-mobile-drawer-action-row",
  mobileDrawerActionLabel: "shell-mobile-drawer-action-label",
  mobileDrawerActionMeta: "shell-mobile-drawer-action-meta",
  mobileDrawerActionCount: "shell-mobile-drawer-action-count",
  tabRegion: "shell-navbar-tab-region",
  tabLink: "shell-navbar-tab-link",
  tabButton: "shell-navbar-tab-button",
  tabActive: "shell-navbar-tab-active",
  utilityRegion: "shell-navbar-utility-region",
  searchWrapper: "shell-navbar-search-wrapper",
  searchToggle: "shell-navbar-search-toggle",
  searchExpanded: "shell-navbar-search-expanded",
  iconButton: "shell-navbar-icon-button",
  dropdown: "shell-navbar-dropdown",
} as const;
