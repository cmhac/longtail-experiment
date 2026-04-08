"use client";

import { Button } from "@heroui/react";
import Link from "next/link";
import React from "react";
import { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";
import { AuthManagementApiError } from "../../lib/api/auth-management-client";
import {
  fetchNotificationList,
  fetchNotificationSummary,
  markAllNotificationsRead,
  markNotificationRead,
  markNotificationUnread,
  requireNotificationSessionToken,
} from "../../lib/api/notification-client";
import type { NotificationListItem } from "../../lib/api/notification-types";
import { loadAuthSessionState } from "../../lib/auth/session-state";
import { formatNotificationBody } from "../../lib/notifications/notification-copy";

export const NotificationsPageClient = (): JSX.Element => {
  const [isLoading, setIsLoading] = useState(true);
  const [isUnauthenticated, setIsUnauthenticated] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [items, setItems] = useState<NotificationListItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);

  const visibleItems = useMemo(() => {
    if (!showUnreadOnly) {
      return items;
    }
    return items.filter((item) => item.unread);
  }, [items, showUnreadOnly]);

  useEffect(() => {
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
          fetchNotificationList(token, { pageSize: 50, unreadOnly: false }),
        ]);
        if (isCancelled) {
          return;
        }
        setUnreadCount(summary.unread_count);
        setItems(listing.items);
      } catch (error) {
        if (isCancelled) {
          return;
        }
        if (error instanceof AuthManagementApiError && error.status === 401) {
          setIsUnauthenticated(true);
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
  }, []);

  if (isLoading) {
    return (
      <p className="text-default-500 text-sm" data-testid="notifications-page-loading">
        Loading notifications...
      </p>
    );
  }

  if (isUnauthenticated) {
    return (
      <div className="grid gap-2" data-testid="notifications-page-unauthenticated">
        <p className="text-default-500 text-sm">Sign in to manage notifications.</p>
        <Link href="/login" className="text-primary text-sm hover:underline">
          Sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-4" data-testid="notifications-page-client">
      <div className="flex flex-wrap items-center gap-2">
        <Button
          size="sm"
          variant={showUnreadOnly ? "primary" : "outline"}
          data-testid="notifications-toggle-unread-only"
          onPress={() => setShowUnreadOnly((previous) => !previous)}
        >
          {showUnreadOnly ? "Showing unread" : "Show unread only"}
        </Button>
        <Button
          size="sm"
          variant="outline"
          data-testid="notifications-mark-all-read"
          onPress={async () => {
            try {
              const state = loadAuthSessionState();
              const token = await requireNotificationSessionToken(state?.sessionToken);
              await markAllNotificationsRead(token);
              setItems((previous) => previous.map((item) => ({ ...item, unread: false })));
              setUnreadCount(0);
            } catch {
              setErrorMessage("Unable to mark all notifications read.");
            }
          }}
        >
          Mark all read
        </Button>
        <span className="text-default-500 text-sm" data-testid="notifications-unread-count">
          Unread: {unreadCount}
        </span>
      </div>

      {errorMessage ? (
        <p className="text-danger text-sm" data-testid="notifications-page-error">
          {errorMessage}
        </p>
      ) : null}

      {visibleItems.length === 0 ? (
        <p className="text-default-500 text-sm" data-testid="notifications-page-empty">
          No notifications to show.
        </p>
      ) : (
        <ul className="grid gap-2" data-testid="notifications-page-list">
          {visibleItems.map((item) => (
            <li
              key={item.notification_id}
              className="rounded-lg border border-default-200 p-3"
              data-testid={`notifications-page-item-${item.notification_id}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-medium text-sm">{item.title}</p>
                  <p className="text-default-500 text-xs">{formatNotificationBody(item)}</p>
                </div>
                <div className="flex gap-1">
                  {item.unread ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      data-testid={`notifications-page-mark-read-${item.notification_id}`}
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
                          setUnreadCount((previous) => Math.max(previous - 1, 0));
                        } catch {
                          setErrorMessage("Unable to update notification state.");
                        }
                      }}
                    >
                      Mark read
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="ghost"
                      data-testid={`notifications-page-mark-unread-${item.notification_id}`}
                      onPress={async () => {
                        try {
                          const state = loadAuthSessionState();
                          const token = await requireNotificationSessionToken(state?.sessionToken);
                          await markNotificationUnread(token, item.notification_id);
                          setItems((previous) =>
                            previous.map((entry) =>
                              entry.notification_id === item.notification_id
                                ? { ...entry, unread: true }
                                : entry,
                            ),
                          );
                          setUnreadCount((previous) => previous + 1);
                        } catch {
                          setErrorMessage("Unable to update notification state.");
                        }
                      }}
                    >
                      Mark unread
                    </Button>
                  )}
                </div>
              </div>
              <Link
                href={item.destination_path}
                className="mt-2 inline-block text-primary text-xs hover:underline"
              >
                View dataset
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
