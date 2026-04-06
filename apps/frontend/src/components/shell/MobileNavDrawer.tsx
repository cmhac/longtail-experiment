"use client";

import { Button } from "@heroui/react";
import React from "react";
import { createPortal } from "react-dom";
import type { JSX } from "react";
import { useEffect } from "react";
import type { PrivilegeLevel } from "../../lib/api/auth-management-types";
import { SHELL_NAVBAR_CLASS_NAMES } from "../../theme/monochrome-theme";
import { MobileNavDrawerAction } from "./MobileNavDrawerAction";

export interface MobileDrawerPrimaryAction {
  key: string;
  label: string;
  testId: string;
  onPress: () => void;
  countValue?: string;
}

interface MobileNavDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onBellPress: () => void;
  unreadNotificationCount: number;
  primaryActions: readonly MobileDrawerPrimaryAction[];
  onSignOutPress: () => void;
  onAdminPress: () => void;
  canAccessAdmin: boolean;
  isSigningOut: boolean;
  authStatus: "signed_in" | "signed_out";
  privilegeLevel: PrivilegeLevel | null;
}

export const MobileNavDrawer = ({
  isOpen,
  onClose,
  onBellPress,
  unreadNotificationCount,
  primaryActions,
  onSignOutPress,
  onAdminPress,
  canAccessAdmin,
  isSigningOut,
  authStatus,
  privilegeLevel,
}: MobileNavDrawerProps): JSX.Element | null => {
  useEffect(() => {
    if (typeof document === "undefined" || !isOpen) {
      return;
    }

    const htmlStyle = document.documentElement.style;
    const bodyStyle = document.body.style;
    const lockedScrollY = window.scrollY;

    const previousHtmlOverflow = htmlStyle.overflow;
    const previousBodyOverflow = bodyStyle.overflow;
    const previousBodyTouchAction = bodyStyle.touchAction;
    const previousBodyPosition = bodyStyle.position;
    const previousBodyTop = bodyStyle.top;
    const previousBodyLeft = bodyStyle.left;
    const previousBodyRight = bodyStyle.right;
    const previousBodyWidth = bodyStyle.width;

    htmlStyle.overflow = "hidden";
    bodyStyle.overflow = "hidden";
    bodyStyle.touchAction = "none";
    bodyStyle.position = "fixed";
    bodyStyle.top = `-${lockedScrollY}px`;
    bodyStyle.left = "0";
    bodyStyle.right = "0";
    bodyStyle.width = "100%";

    return () => {
      htmlStyle.overflow = previousHtmlOverflow;
      bodyStyle.overflow = previousBodyOverflow;
      bodyStyle.touchAction = previousBodyTouchAction;
      bodyStyle.position = previousBodyPosition;
      bodyStyle.top = previousBodyTop;
      bodyStyle.left = previousBodyLeft;
      bodyStyle.right = previousBodyRight;
      bodyStyle.width = previousBodyWidth;
      if (typeof window.scrollTo === "function") {
        try {
          window.scrollTo(0, lockedScrollY);
        } catch {
          return;
        }
      }
    };
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  if (typeof document === "undefined") {
    return null;
  }

  return createPortal(
    <div className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerRoot} data-testid="mobile-nav-drawer-root">
      <button
        type="button"
        className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerBackdrop}
        data-testid="mobile-nav-drawer-backdrop"
        aria-label="Close mobile navigation drawer"
        onClick={onClose}
      />
      <aside
        className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerPanel}
        data-testid="mobile-nav-drawer-panel"
        aria-label="Mobile navigation drawer"
      >
        <div
          className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerHeader}
          data-testid="mobile-nav-drawer-header-row"
        >
          <span
            className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerHeaderBrand}
            data-testid="mobile-nav-drawer-brand"
          >
            Longtail
          </span>
          <Button
            className={`${SHELL_NAVBAR_CLASS_NAMES.iconButton} relative`}
            data-testid="mobile-nav-drawer-bell"
            aria-label={
              unreadNotificationCount > 0
                ? `Notifications (${unreadNotificationCount} unread)`
                : "Notifications"
            }
            isIconOnly
            size="sm"
            variant="ghost"
            onPress={onBellPress}
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
                data-testid="mobile-nav-drawer-bell-badge"
              >
                {unreadNotificationCount > 99 ? "99+" : unreadNotificationCount}
              </span>
            ) : null}
          </Button>
        </div>

        <div
          className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerPrimary}
          data-testid="mobile-nav-drawer-primary-actions"
        >
          {primaryActions.map((action) => (
            <MobileNavDrawerAction
              key={action.key}
              label={action.label}
              testId={action.testId}
              {...(action.countValue ? { countValue: action.countValue } : {})}
              onPress={action.onPress}
            />
          ))}
        </div>

        <div
          className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerFooter}
          data-auth-status={authStatus}
          data-privilege-level={privilegeLevel ?? "none"}
          data-testid="mobile-nav-drawer-footer"
        >
          {canAccessAdmin ? (
            <MobileNavDrawerAction
              label="Admin"
              testId="mobile-nav-drawer-action-admin"
              onPress={onAdminPress}
            />
          ) : null}
          <MobileNavDrawerAction
            label="Sign out"
            testId="mobile-nav-drawer-action-sign-out"
            tone="danger"
            onPress={onSignOutPress}
            isDisabled={isSigningOut}
          />
        </div>
      </aside>
    </div>,
    document.body,
  );
};
