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
import { SHELL_NAVBAR_CLASS_NAMES, SHELL_REGION_CLASS_NAMES } from "../theme/monochrome-theme";
import { type NavbarTabKey, resolveNavbarTabs } from "./navbar-config";

export const SITE_HEADER_VARIANT = "light";

interface SiteHeaderProps {
  activeTab?: NavbarTabKey;
}

export const SiteHeader = ({ activeTab = "home" }: SiteHeaderProps): JSX.Element => {
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const [comparisonCount, setComparisonCount] = useState(0);
  const [hasComparisonStateError, setHasComparisonStateError] = useState(false);
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
    const handleDocumentPointerDown = (event: MouseEvent): void => {
      if (event.target instanceof Node) {
        if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
          setIsProfileMenuOpen(false);
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
                  dropdown coming soon
                </Card>
              ) : null}
            </div>
          </div>
        </nav>
      </Card>
    </header>
  );
};
