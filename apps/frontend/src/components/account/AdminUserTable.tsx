"use client";

import { Button, Card, Table } from "@heroui/react";
import * as React from "react";
import type { JSX } from "react";
import type { AdminUserSummary } from "../../lib/api/auth-management-types";

interface AdminUserTableProps {
  users: AdminUserSummary[];
  isUpdatingUserId: string | null;
  isRevokingUserId: string | null;
  isUpdatingRoleUserId: string | null;
  onToggleStatus: (user: AdminUserSummary) => void;
  onRevokeSessions: (user: AdminUserSummary) => void;
  onToggleAdminRole: (user: AdminUserSummary) => void;
}

export const AdminUserTable = ({
  users,
  isUpdatingUserId,
  isRevokingUserId,
  isUpdatingRoleUserId,
  onToggleStatus,
  onRevokeSessions,
  onToggleAdminRole,
}: AdminUserTableProps): JSX.Element => {
  if (users.length === 0) {
    return <Card className="p-4 text-default-600 text-sm">No users found.</Card>;
  }

  return (
    <Table data-testid="admin-users-table">
      <Table.ScrollContainer>
        <Table.Content aria-label="Admin users" className="min-w-190">
          <Table.Header>
            <Table.Column isRowHeader>Name</Table.Column>
            <Table.Column>Email</Table.Column>
            <Table.Column>Status</Table.Column>
            <Table.Column className="text-end">Actions</Table.Column>
          </Table.Header>
          <Table.Body
            renderEmptyState={() => (
              <div className="p-4 text-default-600 text-sm">No users found.</div>
            )}
          >
            {users.map((user) => {
              const isUpdating = isUpdatingUserId === user.user_id;
              const isRevoking = isRevokingUserId === user.user_id;
              const isUpdatingRole = isUpdatingRoleUserId === user.user_id;
              const nextStatus = user.account_status === "active" ? "deactivated" : "active";
              const nextActionLabel = nextStatus === "deactivated" ? "Deactivate" : "Reactivate";
              const isOwner = user.privilege_level === "owner";
              const roleActionLabel = user.is_admin ? "Revoke admin" : "Grant admin";

              return (
                <Table.Row key={user.user_id} id={user.user_id}>
                  <Table.Cell>
                    <div className="grid gap-1" data-testid={`admin-user-row-${user.user_id}`}>
                      <p className="font-medium text-sm">{user.display_name ?? user.email}</p>
                      {user.privilege_level !== "user" ? (
                        <p
                          className="text-default-500 text-xs"
                          data-testid={`admin-user-role-${user.user_id}`}
                        >
                          {user.privilege_level}
                        </p>
                      ) : null}
                    </div>
                  </Table.Cell>
                  <Table.Cell>
                    <p className="text-default-600 text-xs">{user.email}</p>
                  </Table.Cell>
                  <Table.Cell>
                    <p
                      className="text-default-500 text-xs"
                      data-testid={`admin-user-status-${user.user_id}`}
                    >
                      {user.account_status}
                    </p>
                  </Table.Cell>
                  <Table.Cell>
                    <div className="flex flex-wrap items-center justify-end gap-2">
                      <Button
                        data-testid={`admin-user-status-toggle-${user.user_id}`}
                        isDisabled={isUpdating || isRevoking || isUpdatingRole}
                        size="sm"
                        variant="secondary"
                        onPress={() => onToggleStatus(user)}
                      >
                        {isUpdating ? "Saving..." : nextActionLabel}
                      </Button>
                      <Button
                        data-testid={`admin-user-role-toggle-${user.user_id}`}
                        isDisabled={isUpdating || isRevoking || isUpdatingRole || isOwner}
                        size="sm"
                        variant="outline"
                        onPress={() => onToggleAdminRole(user)}
                      >
                        {isUpdatingRole
                          ? "Saving role..."
                          : isOwner
                            ? "Owner protected"
                            : roleActionLabel}
                      </Button>
                      <Button
                        data-testid={`admin-user-revoke-${user.user_id}`}
                        isDisabled={isUpdating || isRevoking || isUpdatingRole}
                        size="sm"
                        variant="danger-soft"
                        onPress={() => onRevokeSessions(user)}
                      >
                        {isRevoking ? "Revoking..." : "Revoke sessions"}
                      </Button>
                    </div>
                  </Table.Cell>
                </Table.Row>
              );
            })}
          </Table.Body>
        </Table.Content>
      </Table.ScrollContainer>
    </Table>
  );
};
