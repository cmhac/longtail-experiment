"use client";

import { Button, Card } from "@heroui/react";
import Link from "next/link";
import React from "react";
import { useEffect, useState } from "react";
import type { JSX } from "react";
import { AuthManagementApiError } from "../../lib/api/auth-management-client";
import {
  fetchNotificationList,
  fetchNotificationSummary,
  markNotificationRead,
  requireNotificationSessionToken,
} from "../../lib/api/notification-client";
import type { NotificationListItem } from "../../lib/api/notification-types";
import { loadAuthSessionState } from "../../lib/auth/session-state";

interface NotificationsDropdownProps {
  isOpen: boolean;
  onClose: () => void;
  onUnreadCountChange?: (count: number) => void;
}

export const NotificationsDropdown = ({
  isOpen,
  onClose,
  onUnreadCountChange,
}: NotificationsDropdownProps): JSX.Element | null => {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [items, setItems] = useState<NotificationListItem[]>([]);
  const [isUnauthenticated, setIsUnauthenticated] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    let isCancelled = false;
    const load = async (): Promise<void> => {
      setIsLoading(true);
      setErrorMessage(null);
      setIsUnauthenticated(false);
      try {
        const state = loadAuthSessionState();
        const token = await requireNotificationSessionToken(state?.sessionToken);
        const [summary, listing] = await Promise.all([
          fetchNotificationSummary(token),
          fetchNotificationList(token, { pageSize: 5, unreadOnly: false }),
        ]);
        if (isCancelled) {
          return;
        }
        setItems(listing.items);
        onUnreadCountChange?.(summary.unread_count);
      } catch (error) {
        if (isCancelled) {
          return;
        }
        if (error instanceof AuthManagementApiError && error.status === 401) {
          setIsUnauthenticated(true);
          onUnreadCountChange?.(0);
          return;
        }
        setErrorMessage("Unable to load notifications.");
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    void load();
    return () => {
      isCancelled = true;
    };
  }, [isOpen, onUnreadCountChange]);

  if (!isOpen) {
    return null;
  }

  return (
    <Card
      id="navbar-notifications-dropdown"
      role="menu"
      className="absolute top-full right-0 z-[240] mt-2 w-88 max-w-[calc(100vw-2rem)] rounded-xl border border-default-200 bg-content1 p-3 shadow-md"
      data-testid="navbar-notifications-dropdown"
      variant="default"
    >
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-medium text-sm">Notifications</h3>
        <Link
          href="/notifications"
          className="text-primary text-xs hover:underline"
          data-testid="navbar-notifications-manage-link"
          onClick={onClose}
        >
          View all
        </Link>
      </div>

      {isLoading ? (
        <p className="text-default-500 text-sm" data-testid="navbar-notifications-loading">
          Loading notifications...
        </p>
      ) : null}

      {!isLoading && isUnauthenticated ? (
        <div className="grid gap-2" data-testid="navbar-notifications-unauthenticated">
          <p className="text-default-500 text-sm">Sign in to view notifications.</p>
          <Link href="/login" className="text-primary text-sm hover:underline" onClick={onClose}>
            Sign in
          </Link>
        </div>
      ) : null}

      {!isLoading && errorMessage ? (
        <p className="text-danger text-sm" data-testid="navbar-notifications-error">
          {errorMessage}
        </p>
      ) : null}

      {!isLoading && !isUnauthenticated && !errorMessage && items.length === 0 ? (
        <p className="text-default-500 text-sm" data-testid="navbar-notifications-empty">
          No notifications yet.
        </p>
      ) : null}

      {!isLoading && !isUnauthenticated && !errorMessage && items.length > 0 ? (
        <ul className="grid gap-2" data-testid="navbar-notifications-list">
          {items.map((item) => (
            <li key={item.notification_id} className="rounded-lg border border-default-200 p-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-medium text-sm">{item.title}</p>
                  <p className="text-default-500 text-xs">{item.body}</p>
                </div>
                {item.unread ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    data-testid={`navbar-notification-mark-read-${item.notification_id}`}
                    onPress={async () => {
                      try {
                        const state = loadAuthSessionState();
                        const token = await requireNotificationSessionToken(state?.sessionToken);
                        await markNotificationRead(token, item.notification_id);
                        setItems((previous) =>
                          previous.map((entry) =>
                            entry.notification_id === item.notification_id
                              ? { ...entry, unread: false }
                              : entry,
                          ),
                        );
                        onUnreadCountChange?.(
                          Math.max(items.filter((entry) => entry.unread).length - 1, 0),
                        );
                      } catch {
                        setErrorMessage("Unable to update notification state.");
                      }
                    }}
                  >
                    Mark read
                  </Button>
                ) : null}
              </div>
              <Link
                href={item.destination_path}
                className="mt-1 inline-block text-primary text-xs hover:underline"
                onClick={onClose}
              >
                View dataset
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
    </Card>
  );
};
