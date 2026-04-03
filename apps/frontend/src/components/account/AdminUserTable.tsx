"use client";

import { Button, Card } from "@heroui/react";
import * as React from "react";
import type { JSX } from "react";
import type { AdminUserSummary } from "../../lib/api/auth-management-types";

interface AdminUserTableProps {
  users: AdminUserSummary[];
  isUpdatingUserId: string | null;
  isRevokingUserId: string | null;
  onToggleStatus: (user: AdminUserSummary) => void;
  onRevokeSessions: (user: AdminUserSummary) => void;
}

export const AdminUserTable = ({
  users,
  isUpdatingUserId,
  isRevokingUserId,
  onToggleStatus,
  onRevokeSessions,
}: AdminUserTableProps): JSX.Element => {
  if (users.length === 0) {
    return <Card className="p-4 text-default-600 text-sm">No users found.</Card>;
  }

  return (
    <div className="grid gap-2" data-testid="admin-users-table">
      {users.map((user) => {
        const isUpdating = isUpdatingUserId === user.user_id;
        const isRevoking = isRevokingUserId === user.user_id;
        const nextStatus = user.account_status === "active" ? "deactivated" : "active";
        const nextActionLabel = nextStatus === "deactivated" ? "Deactivate" : "Reactivate";

        return (
          <Card
            key={user.user_id}
            className="grid gap-3 border border-default-200 p-4 sm:grid-cols-[1fr_auto]"
            data-testid={`admin-user-row-${user.user_id}`}
          >
            <div className="grid gap-1">
              <p className="font-medium text-sm">{user.display_name ?? user.email}</p>
              <p className="text-default-600 text-xs">{user.email}</p>
              <p
                className="text-default-500 text-xs"
                data-testid={`admin-user-status-${user.user_id}`}
              >
                Status: {user.account_status}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2 sm:justify-end">
              <Button
                data-testid={`admin-user-status-toggle-${user.user_id}`}
                isDisabled={isUpdating || isRevoking}
                size="sm"
                variant="outline"
                onPress={() => onToggleStatus(user)}
              >
                {isUpdating ? "Saving..." : nextActionLabel}
              </Button>
              <Button
                data-testid={`admin-user-revoke-${user.user_id}`}
                isDisabled={isUpdating || isRevoking}
                size="sm"
                variant="danger-soft"
                onPress={() => onRevokeSessions(user)}
              >
                {isRevoking ? "Revoking..." : "Revoke sessions"}
              </Button>
            </div>
          </Card>
        );
      })}
    </div>
  );
};
