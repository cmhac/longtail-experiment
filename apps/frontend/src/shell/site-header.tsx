"use client";

import { Button, Card } from "@heroui/react";
import Link from "next/link";
import React from "react";
import { useEffect, useRef, useState } from "react";
import type { JSX } from "react";
import { UnifiedSearchSurface } from "../components/discovery/UnifiedSearchSurface";
import { NotificationsDropdown } from "../components/notifications/NotificationsDropdown";
import {
  COMPARISON_STATE_EVENT,
  ComparisonStateCorruptedError,
  getComparisonCount,
} from "../components/discovery/comparison-state";
import { logoutAccount } from "../lib/api/auth-management-client";
import {
  type AuthSessionState,
  clearAuthSessionState,
  loadAuthSessionState,
} from "../lib/auth/session-state";
import { SHELL_NAVBAR_CLASS_NAMES, SHELL_REGION_CLASS_NAMES } from "../theme/monochrome-theme";
import { type NavbarTabKey, resolveNavbarTabs } from "./navbar-config";

interface SiteHeaderProps {
  activeTab?: NavbarTabKey;
}

export const SiteHeader = ({ activeTab = "home" }: SiteHeaderProps): JSX.Element => {
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const [comparisonCount, setComparisonCount] = useState(0);
  const [hasComparisonStateError, setHasComparisonStateError] = useState(false);
  const [authSession, setAuthSession] = useState<AuthSessionState | null>(null);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement | null>(null);
  const searchControlRef = useRef<HTMLDivElement | null>(null);
  const tabs = resolveNavbarTabs(activeTab);

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

            <Button
              className={`${SHELL_NAVBAR_CLASS_NAMES.iconButton} relative`}
              data-testid="navbar-notifications-control"
              aria-label={
                unreadNotificationCount > 0
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
              {unreadNotificationCount > 0 ? (
                <span
                  className="absolute top-1 right-1 min-w-[0.95rem] rounded-full bg-danger px-1 text-center text-[0.62rem] text-white leading-4"
                  data-testid="navbar-notifications-badge"
                >
                  {unreadNotificationCount > 99 ? "99+" : unreadNotificationCount}
                </span>
              ) : null}
            </Button>

            <div className="relative" data-testid="navbar-notifications-wrapper">
              <NotificationsDropdown
                isOpen={isNotificationsOpen}
                onClose={() => setIsNotificationsOpen(false)}
                onUnreadCountChange={setUnreadNotificationCount}
              />
            </div>

            <Button
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
                if (typeof window !== "undefined") {
                  window.location.assign("/comparison");
                }
              }}
            >
              <span className="shell-navbar-comparison-label">Compare</span>
              <span className="shell-navbar-comparison-count" data-testid="navbar-comparison-count">
                {hasComparisonStateError ? "!" : comparisonCount}
              </span>
            </Button>

            <div className="shell-navbar-profile-wrapper" ref={profileMenuRef}>
              <Button
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
                  {authSession ? (
                    <div className="grid gap-2 p-3" data-testid="header-auth-signed-in">
                      <p className="text-default-600 text-xs" data-testid="header-auth-email">
                        {authSession.user.email}
                      </p>
                      {authSession.user.privilege_level === "admin" ||
                      authSession.user.privilege_level === "owner" ? (
                        <p className="text-default-500 text-xs" data-testid="header-auth-role-chip">
                          {authSession.user.privilege_level === "owner" ? "Owner" : "Admin"}
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
                          if (typeof window !== "undefined") {
                            window.location.assign("/settings");
                          }
                        }}
                      >
                        Account
                      </Button>
                      {authSession.user.privilege_level === "admin" ||
                      authSession.user.privilege_level === "owner" ? (
                        <Button
                          className="justify-center border border-default-300 bg-default-100 text-foreground dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100"
                          data-testid="header-auth-admin-button"
                          fullWidth
                          size="sm"
                          variant="outline"
                          onPress={() => {
                            setIsProfileMenuOpen(false);
                            if (typeof window !== "undefined") {
                              window.location.assign("/admin");
                            }
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
                        onPress={async () => {
                          if (isSigningOut) {
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
                            setIsProfileMenuOpen(false);
                            if (typeof window !== "undefined") {
                              window.location.assign("/");
                            }
                          }
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
          </div>
        </nav>
      </Card>
    </header>
  );
};
