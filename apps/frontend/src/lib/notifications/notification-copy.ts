import type { NotificationListItem } from "../api/notification-types";

export const NOTIFICATION_CONFIDENCE_SCORE_THRESHOLD = 0.7;

export const formatNotificationBody = (item: NotificationListItem): string => {
  const base = `${item.dataset_id}: ${item.previous_direction} to ${item.current_direction}`;
  const confidence = item.confidence_score;
  if (typeof confidence !== "number" || confidence < NOTIFICATION_CONFIDENCE_SCORE_THRESHOLD) {
    return base;
  }
  return `${base} (confidence ${confidence.toFixed(2)})`;
};
