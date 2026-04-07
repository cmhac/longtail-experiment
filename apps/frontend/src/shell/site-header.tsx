"use client";

import { Button, Card } from "@heroui/react";
import Link from "next/link";
import React from "react";
import { useEffect, useRef, useState } from "react";
import type { JSX } from "react";
import { UnifiedSearchSurface } from "../components/discovery/UnifiedSearchSurface";
import {
  COMPARISON_STATE_EVENT,
  ComparisonStateCorruptedError,
  getComparisonCount,
} from "../components/discovery/comparison-state";
import { NotificationsDropdown } from "../components/notifications/NotificationsDropdown";
import {
  type MobileDrawerPrimaryAction,
  MobileNavDrawer,
} from "../components/shell/MobileNavDrawer";
import { AuthManagementApiError, logoutAccount } from "../lib/api/auth-management-client";
import type { PrivilegeLevel } from "../lib/api/auth-management-types";
import {
  fetchNotificationSummary,
  requireNotificationSessionToken,
} from "../lib/api/notification-client";
import {
  type AuthSessionState,
  clearAuthSessionState,
  loadAuthSessionState,
} from "../lib/auth/session-state";
import { navigateTo } from "../lib/navigation-client";
import { SHELL_NAVBAR_CLASS_NAMES, SHELL_REGION_CLASS_NAMES } from "../theme/monochrome-theme";
import {
  MOBILE_DRAWER_MEDIA_QUERY,
  MOBILE_DRAWER_PRIMARY_ITEMS,
  type NavbarTabKey,
  isMobileDrawerViewportWidth,
  resolveNavbarTabs,
} from "./navbar-config";

interface SiteHeaderProps {
  activeTab?: NavbarTabKey;
}

const isAdminPrivilege = (privilegeLevel: PrivilegeLevel | null): boolean => {
  return privilegeLevel === "admin" || privilegeLevel === "owner";
};

const evaluateMobileDrawerEnabled = (): boolean => {
  if (typeof window === "undefined") {
    return false;
  }

  if (typeof window.matchMedia === "function") {
    return window.matchMedia(MOBILE_DRAWER_MEDIA_QUERY).matches;
  }

  return isMobileDrawerViewportWidth(window.innerWidth);
};

export const SiteHeader = ({ activeTab = "home" }: SiteHeaderProps): JSX.Element => {
  const [hasHydrated, setHasHydrated] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const [comparisonCount, setComparisonCount] = useState(0);
  const [hasComparisonStateError, setHasComparisonStateError] = useState(false);
  const [authSession, setAuthSession] = useState<AuthSessionState | null>(null);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);
  const [isMobileDrawerEnabled, setIsMobileDrawerEnabled] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement | null>(null);
  const searchControlRef = useRef<HTMLDivElement | null>(null);
  const tabs = resolveNavbarTabs(activeTab);

  const privilegeLevel = authSession?.user?.privilege_level ?? null;
  const canAccessAdmin = isAdminPrivilege(privilegeLevel);
  const comparisonCountDisplay = hasComparisonStateError ? "!" : `${comparisonCount}`;

  const navigateToPath = (path: string): void => {
    navigateTo(path);
  };

  const closeDrawerAndNavigate = (destination: string): void => {
    setIsMobileDrawerOpen(false);
    navigateToPath(destination);
  };

  const handleDrawerDestinationPress = (destination: string, isProtected: boolean): void => {
    if (isProtected && !authSession?.sessionToken) {
      closeDrawerAndNavigate("/login");
      return;
    }
    closeDrawerAndNavigate(destination);
  };

  const handleSignOut = async (): Promise<void> => {
    if (isSigningOut) {
      return;
    }

    setIsProfileMenuOpen(false);
    setIsMobileDrawerOpen(false);

    if (!authSession?.sessionToken) {
      navigateToPath("/");
      return;
    }

    setIsSigningOut(true);
    try {
      await logoutAccount(authSession.sessionToken);
    } catch {
      // ignore logout failures and clear client session state regardless
    } finally {
      clearAuthSessionState();
      setAuthSession(null);
      setIsSigningOut(false);
      setIsNotificationsOpen(false);
      setIsSearchExpanded(false);
      navigateToPath("/");
    }
  };

  const drawerPrimaryActions: readonly MobileDrawerPrimaryAction[] =
    MOBILE_DRAWER_PRIMARY_ITEMS.map((item) => {
      return {
        key: item.key,
        label: item.label,
        testId: `mobile-nav-drawer-action-${item.key}`,
        ...(item.key === "comparison" ? { countValue: comparisonCountDisplay } : {}),
        onPress: () => {
          handleDrawerDestinationPress(item.destination, item.isProtected);
        },
      };
    });

  useEffect(() => {
    setHasHydrated(true);
  }, []);

  useEffect(() => {
    const syncComparisonCount = (): void => {
      try {
        setComparisonCount(getComparisonCount());
        setHasComparisonStateError(false);
      } catch (error) {
        if (error instanceof ComparisonStateCorruptedError) {
          setHasComparisonStateError(true);
        }
      }
    };

    syncComparisonCount();

    window.addEventListener(COMPARISON_STATE_EVENT, syncComparisonCount);
    window.addEventListener("storage", syncComparisonCount);
    return () => {
      window.removeEventListener(COMPARISON_STATE_EVENT, syncComparisonCount);
      window.removeEventListener("storage", syncComparisonCount);
    };
  }, []);

  useEffect(() => {
    const syncAuthState = (): void => {
      setAuthSession(loadAuthSessionState());
    };

    syncAuthState();
    window.addEventListener("storage", syncAuthState);
    return () => {
      window.removeEventListener("storage", syncAuthState);
    };
  }, []);

  useEffect(() => {
    let isCancelled = false;

    const preloadUnreadSummary = async (): Promise<void> => {
      const sessionToken = authSession?.sessionToken;
      if (!sessionToken) {
        setUnreadNotificationCount(0);
        return;
      }

      try {
        const token = await requireNotificationSessionToken(sessionToken);
        const summary = await fetchNotificationSummary(token);
        if (!isCancelled) {
          setUnreadNotificationCount(summary.unread_count);
        }
      } catch (error) {
        if (isCancelled) {
          return;
        }
        if (error instanceof AuthManagementApiError && error.status === 401) {
          setUnreadNotificationCount(0);
        }
      }
    };

    void preloadUnreadSummary();
    return () => {
      isCancelled = true;
    };
  }, [authSession?.sessionToken]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const update = (): void => {
      setIsMobileDrawerEnabled(evaluateMobileDrawerEnabled());
    };

    update();

    window.addEventListener("resize", update);

    const mediaQuery =
      typeof window.matchMedia === "function" ? window.matchMedia(MOBILE_DRAWER_MEDIA_QUERY) : null;

    const handleChange = (): void => {
      update();
    };

    mediaQuery?.addEventListener("change", handleChange);

    return () => {
      window.removeEventListener("resize", update);
      mediaQuery?.removeEventListener("change", handleChange);
    };
  }, []);

  useEffect(() => {
    if (!isMobileDrawerEnabled) {
      setIsMobileDrawerOpen(false);
    }
  }, [isMobileDrawerEnabled]);

  useEffect(() => {
    const handleDocumentPointerDown = (event: MouseEvent): void => {
      if (event.target instanceof Node) {
        const targetElement = event.target instanceof Element ? event.target : null;
        if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
          setIsProfileMenuOpen(false);
        }

        if (!targetElement?.closest("[data-testid='navbar-notifications-wrapper']")) {
          setIsNotificationsOpen(false);
        }

        if (searchControlRef.current && !searchControlRef.current.contains(event.target)) {
          setIsSearchExpanded(false);
        }
      }
    };

    document.addEventListener("mousedown", handleDocumentPointerDown);

    return () => {
      document.removeEventListener("mousedown", handleDocumentPointerDown);
    };
  }, []);

  return (
    <header
      className={SHELL_REGION_CLASS_NAMES.header}
      data-shell-region="header"
      data-testid="shell-header"
    >
      <Card
        className={`${SHELL_NAVBAR_CLASS_NAMES.card} shell-navbar-surface rounded-none border-x-0 border-t-0`}
        data-testid="navbar-container"
        variant="transparent"
      >
        <nav className={SHELL_NAVBAR_CLASS_NAMES.nav} aria-label="Primary">
          <div className={SHELL_NAVBAR_CLASS_NAMES.brandRegion}>
            <Link
              href="/"
              className={SHELL_NAVBAR_CLASS_NAMES.brandLink}
              data-testid="navbar-brand-link"
            >
              Longtail
            </Link>
          </div>

          <div className={SHELL_NAVBAR_CLASS_NAMES.tabRegion}>
            {tabs.map((tab) => {
              if (tab.isEnabled && tab.href) {
                return (
                  <Link
                    key={tab.key}
                    href={tab.href}
                    className={`${SHELL_NAVBAR_CLASS_NAMES.tabLink} ${
                      tab.isActive ? SHELL_NAVBAR_CLASS_NAMES.tabActive : ""
                    } rounded-full px-3 py-2 text-sm transition-colors hover:bg-background/70 hover:text-foreground`.trim()}
                    aria-current={tab.isActive ? "page" : undefined}
                    data-testid={`navbar-tab-${tab.key}`}
                  >
                    {tab.label}
                  </Link>
                );
              }

              return (
                <Button
                  key={tab.key}
                  className={SHELL_NAVBAR_CLASS_NAMES.tabButton}
                  data-testid={`navbar-tab-${tab.key}`}
                  isDisabled
                  size="sm"
                  variant="ghost"
                >
                  {tab.label}
                </Button>
              );
            })}
          </div>

          <div className={SHELL_NAVBAR_CLASS_NAMES.utilityRegion}>
            <div className={SHELL_NAVBAR_CLASS_NAMES.searchWrapper} ref={searchControlRef}>
              {isSearchExpanded ? (
                <div
                  id="navbar-search-expanded"
                  className={SHELL_NAVBAR_CLASS_NAMES.searchExpanded}
                  data-testid="navbar-search-expanded"
                >
                  <UnifiedSearchSurface
                    onQuerySubmitted={() => {
                      setIsSearchExpanded(false);
                    }}
                    submitPath="/search"
                    variant="navbar"
                  />
                </div>
              ) : (
                <Button
                  id="navbar-search-control-button"
                  className={`${SHELL_NAVBAR_CLASS_NAMES.iconButton} ${SHELL_NAVBAR_CLASS_NAMES.searchToggle}`}
                  data-testid="navbar-search-control"
                  aria-label="Search"
                  aria-controls="navbar-search-expanded"
                  aria-expanded="false"
                  isIconOnly
                  size="sm"
                  variant="ghost"
                  onPress={() => {
                    setIsSearchExpanded(true);
                  }}
                >
                  <svg aria-hidden="true" viewBox="0 0 24 24" role="img">
                    <path
                      d="M10.5 3a7.5 7.5 0 0 1 5.97 12.05l4.74 4.74-1.41 1.41-4.74-4.74A7.5 7.5 0 1 1 10.5 3Zm0 2a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11Z"
                      fill="currentColor"
                    />
                  </svg>
                </Button>
              )}
            </div>

            <div className="relative" data-testid="navbar-notifications-wrapper">
              <Button
                id="navbar-notifications-control-button"
                className={`${SHELL_NAVBAR_CLASS_NAMES.iconButton} shell-navbar-notifications-control relative`}
                data-testid="navbar-notifications-control"
                aria-label={
                  hasHydrated && unreadNotificationCount > 0
                    ? `Notifications (${unreadNotificationCount} unread)`
                    : "Notifications"
                }
                aria-controls="navbar-notifications-dropdown"
                aria-expanded={isNotificationsOpen ? "true" : "false"}
                isIconOnly
                size="sm"
                variant="ghost"
                onPress={() => {
                  setIsNotificationsOpen((previous) => !previous);
                }}
              >
                <svg aria-hidden="true" viewBox="0 0 24 24" role="img">
                  <path
                    d="M12 3a5 5 0 0 0-5 5v2.26c0 .66-.2 1.31-.56 1.86L5 14v1h14v-1l-1.44-1.88A3.2 3.2 0 0 1 17 10.26V8a5 5 0 0 0-5-5Zm0 19a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Z"
                    fill="currentColor"
                  />
                </svg>
                {hasHydrated && unreadNotificationCount > 0 ? (
                  <span
                    className="absolute top-1 right-1 min-w-[0.95rem] rounded-full bg-danger px-1 text-center text-[0.62rem] text-white leading-4"
                    data-testid="navbar-notifications-badge"
                  >
                    {unreadNotificationCount > 99 ? "99+" : unreadNotificationCount}
                  </span>
                ) : null}
              </Button>

              <NotificationsDropdown
                isOpen={isNotificationsOpen}
                onClose={() => setIsNotificationsOpen(false)}
                onUnreadCountChange={setUnreadNotificationCount}
              />
            </div>

            <Button
              id="navbar-comparison-control-button"
              className={`shell-navbar-comparison-link${
                comparisonCount > 0 && !hasComparisonStateError ? " is-active" : ""
              }`}
              data-testid="navbar-comparison-link"
              aria-label={
                hasComparisonStateError
                  ? "Comparison state needs reset"
                  : `Comparison datasets selected: ${comparisonCount}`
              }
              size="sm"
              variant="ghost"
              onPress={() => {
                navigateToPath("/comparison");
              }}
            >
              <span className="shell-navbar-comparison-label">Compare</span>
              <span className="shell-navbar-comparison-count" data-testid="navbar-comparison-count">
                {comparisonCountDisplay}
              </span>
            </Button>

            <div className="shell-navbar-profile-wrapper" ref={profileMenuRef}>
              <Button
                id="navbar-profile-control-button"
                className={SHELL_NAVBAR_CLASS_NAMES.iconButton}
                data-testid="navbar-profile-control"
                aria-label="Profile"
                aria-expanded={isProfileMenuOpen ? "true" : "false"}
                aria-controls="navbar-profile-dropdown"
                isIconOnly
                size="sm"
                variant="ghost"
                onPress={() => {
                  setIsProfileMenuOpen((previous) => !previous);
                }}
              >
                <svg aria-hidden="true" viewBox="0 0 24 24" role="img">
                  <path
                    d="M12 12a4.5 4.5 0 1 0-4.5-4.5A4.5 4.5 0 0 0 12 12Zm0 2c-3.8 0-7 2-7 4.5V21h14v-2.5c0-2.5-3.2-4.5-7-4.5Z"
                    fill="currentColor"
                  />
                </svg>
              </Button>

              {isProfileMenuOpen ? (
                <Card
                  id="navbar-profile-dropdown"
                  role="menu"
                  className={`${SHELL_NAVBAR_CLASS_NAMES.dropdown} rounded-xl`}
                  data-testid="navbar-profile-dropdown"
                  variant="default"
                >
                  {authSession?.user ? (
                    <div className="grid gap-2 p-3" data-testid="header-auth-signed-in">
                      <p className="text-default-600 text-xs" data-testid="header-auth-email">
                        {authSession.user.email}
                      </p>
                      {canAccessAdmin ? (
                        <p className="text-default-500 text-xs" data-testid="header-auth-role-chip">
                          {privilegeLevel === "owner" ? "Owner" : "Admin"}
                        </p>
                      ) : null}
                      <Button
                        className="justify-center border border-default-300 bg-default-100 text-foreground dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100"
                        data-testid="header-auth-account-button"
                        fullWidth
                        size="sm"
                        variant="outline"
                        onPress={() => {
                          setIsProfileMenuOpen(false);
                          navigateToPath("/settings");
                        }}
                      >
                        Account
                      </Button>
                      {canAccessAdmin ? (
                        <Button
                          className="justify-center border border-default-300 bg-default-100 text-foreground dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100"
                          data-testid="header-auth-admin-button"
                          fullWidth
                          size="sm"
                          variant="outline"
                          onPress={() => {
                            setIsProfileMenuOpen(false);
                            navigateToPath("/admin");
                          }}
                        >
                          Admin
                        </Button>
                      ) : null}
                      <Button
                        className="justify-center"
                        data-testid="header-auth-sign-out"
                        fullWidth
                        isDisabled={isSigningOut}
                        size="sm"
                        variant="danger-soft"
                        onPress={() => {
                          void handleSignOut();
                        }}
                      >
                        Sign out
                      </Button>
                    </div>
                  ) : (
                    <div className="grid gap-2 p-3" data-testid="header-auth-signed-out">
                      <Link href="/login" onClick={() => setIsProfileMenuOpen(false)}>
                        Sign in
                      </Link>
                      <Link href="/register" onClick={() => setIsProfileMenuOpen(false)}>
                        Create account
                      </Link>
                    </div>
                  )}
                </Card>
              ) : null}
            </div>

            <Button
              id="mobile-nav-drawer-trigger-button"
              className={`${SHELL_NAVBAR_CLASS_NAMES.iconButton} ${SHELL_NAVBAR_CLASS_NAMES.mobileDrawerTrigger}`}
              data-testid="mobile-nav-drawer-trigger"
              aria-label="Open navigation menu"
              aria-controls="mobile-nav-drawer-panel"
              aria-expanded={isMobileDrawerOpen ? "true" : "false"}
              isDisabled={!isMobileDrawerEnabled}
              isIconOnly
              size="sm"
              variant="ghost"
              onPress={() => {
                if (!isMobileDrawerEnabled) {
                  return;
                }
                setIsSearchExpanded(false);
                setIsProfileMenuOpen(false);
                setIsNotificationsOpen(false);
                setIsMobileDrawerOpen((previous) => !previous);
              }}
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" role="img">
                <path
                  d="M4 6.5h16v2H4v-2Zm0 4.75h16v2H4v-2Zm0 4.75h16v2H4v-2Z"
                  fill="currentColor"
                />
              </svg>
            </Button>
          </div>
        </nav>

        <MobileNavDrawer
          isOpen={isMobileDrawerOpen && isMobileDrawerEnabled}
          onClose={() => {
            setIsMobileDrawerOpen(false);
          }}
          onBellPress={() => {
            setIsMobileDrawerOpen(false);
            navigateToPath("/notifications");
          }}
          unreadNotificationCount={hasHydrated ? unreadNotificationCount : 0}
          primaryActions={drawerPrimaryActions}
          onSignOutPress={() => {
            void handleSignOut();
          }}
          onAdminPress={() => {
            handleDrawerDestinationPress("/admin", true);
          }}
          canAccessAdmin={canAccessAdmin}
          isSigningOut={isSigningOut}
          authStatus={authSession ? "signed_in" : "signed_out"}
          privilegeLevel={privilegeLevel}
        />
      </Card>
    </header>
  );
};
