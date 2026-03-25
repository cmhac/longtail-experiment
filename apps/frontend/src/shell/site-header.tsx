"use client";

import Link from "next/link";
import React from "react";
import { useEffect, useRef, useState } from "react";
import type { JSX } from "react";
import { UnifiedSearchSurface } from "../components/discovery/UnifiedSearchSurface";
import { SHELL_NAVBAR_CLASS_NAMES, SHELL_REGION_CLASS_NAMES } from "../theme/monochrome-theme";
import { type NavbarTabKey, resolveNavbarTabs } from "./navbar-config";

export const SITE_HEADER_VARIANT = "light";

interface SiteHeaderProps {
  activeTab?: NavbarTabKey;
}

export const SiteHeader = ({ activeTab = "home" }: SiteHeaderProps): JSX.Element => {
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement | null>(null);
  const searchControlRef = useRef<HTMLDivElement | null>(null);
  const tabs = resolveNavbarTabs(activeTab);

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
      <div className={SHELL_NAVBAR_CLASS_NAMES.card} data-testid="navbar-container">
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
                    }`.trim()}
                    aria-current={tab.isActive ? "page" : undefined}
                    data-testid={`navbar-tab-${tab.key}`}
                  >
                    {tab.label}
                  </Link>
                );
              }

              return (
                <button
                  key={tab.key}
                  type="button"
                  className={SHELL_NAVBAR_CLASS_NAMES.tabButton}
                  data-testid={`navbar-tab-${tab.key}`}
                  disabled
                  aria-disabled="true"
                >
                  {tab.label}
                </button>
              );
            })}
          </div>

          <div className={SHELL_NAVBAR_CLASS_NAMES.utilityRegion}>
            <div className={SHELL_NAVBAR_CLASS_NAMES.searchWrapper} ref={searchControlRef}>
              <button
                type="button"
                className={`${SHELL_NAVBAR_CLASS_NAMES.iconButton} ${SHELL_NAVBAR_CLASS_NAMES.searchToggle}`}
                data-testid="navbar-search-control"
                aria-label="Search"
                aria-controls="navbar-search-expanded"
                aria-expanded={isSearchExpanded ? "true" : "false"}
                onClick={() => {
                  setIsSearchExpanded((previous) => !previous);
                }}
              >
                <svg aria-hidden="true" viewBox="0 0 24 24" role="img">
                  <path
                    d="M10.5 3a7.5 7.5 0 0 1 5.97 12.05l4.74 4.74-1.41 1.41-4.74-4.74A7.5 7.5 0 1 1 10.5 3Zm0 2a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11Z"
                    fill="currentColor"
                  />
                </svg>
              </button>

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
              ) : null}
            </div>

            <div className="shell-navbar-profile-wrapper" ref={profileMenuRef}>
              <button
                type="button"
                className={SHELL_NAVBAR_CLASS_NAMES.iconButton}
                data-testid="navbar-profile-control"
                aria-label="Profile"
                aria-expanded={isProfileMenuOpen ? "true" : "false"}
                aria-controls="navbar-profile-dropdown"
                onClick={() => {
                  setIsProfileMenuOpen((previous) => !previous);
                }}
              >
                <svg aria-hidden="true" viewBox="0 0 24 24" role="img">
                  <path
                    d="M12 12a4.5 4.5 0 1 0-4.5-4.5A4.5 4.5 0 0 0 12 12Zm0 2c-3.8 0-7 2-7 4.5V21h14v-2.5c0-2.5-3.2-4.5-7-4.5Z"
                    fill="currentColor"
                  />
                </svg>
              </button>

              {isProfileMenuOpen ? (
                <div
                  id="navbar-profile-dropdown"
                  role="menu"
                  className={SHELL_NAVBAR_CLASS_NAMES.dropdown}
                  data-testid="navbar-profile-dropdown"
                >
                  dropdown coming soon
                </div>
              ) : null}
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
};
