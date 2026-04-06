"use client";

import { Button } from "@heroui/react";
import React from "react";
import { useMemo, useState } from "react";
import type { JSX } from "react";
import { AuthManagementApiError } from "../../lib/api/auth-management-client";
import {
  createNotificationSubscription,
  deleteNotificationSubscription,
  requireNotificationSessionToken,
} from "../../lib/api/notification-client";
import { loadAuthSessionState } from "../../lib/auth/session-state";

interface NotificationSubscriptionControlProps {
  datasetId: string;
  initiallySubscribed?: boolean;
  className?: string;
}

export const NotificationSubscriptionControl = ({
  datasetId,
  initiallySubscribed = false,
  className,
}: NotificationSubscriptionControlProps): JSX.Element => {
  const [isSubscribed, setIsSubscribed] = useState(initiallySubscribed);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const buttonLabel = useMemo(() => {
    return isSubscribed ? "Unfollow Alerts" : "Follow Alerts";
  }, [isSubscribed]);

  return (
    <div className={className} data-testid="notification-subscription-control">
      <Button
        data-testid="notification-subscription-toggle"
        size="sm"
        variant={isSubscribed ? "outline" : "primary"}
        isDisabled={isSubmitting}
        onPress={async () => {
          setErrorMessage(null);
          setIsSubmitting(true);
          try {
            const state = loadAuthSessionState();
            const token = await requireNotificationSessionToken(state?.sessionToken);
            if (isSubscribed) {
              await deleteNotificationSubscription(token, datasetId);
              setIsSubscribed(false);
            } else {
              await createNotificationSubscription(token, { dataset_id: datasetId });
              setIsSubscribed(true);
            }
          } catch (error) {
            if (
              error instanceof AuthManagementApiError &&
              error.status === 401 &&
              typeof window !== "undefined"
            ) {
              window.location.assign("/login");
              return;
            }
            setErrorMessage("Unable to update alerts right now.");
          } finally {
            setIsSubmitting(false);
          }
        }}
      >
        {buttonLabel}
      </Button>
      {errorMessage ? (
        <p className="mt-1 text-danger text-xs" data-testid="notification-subscription-error">
          {errorMessage}
        </p>
      ) : null}
    </div>
  );
};
