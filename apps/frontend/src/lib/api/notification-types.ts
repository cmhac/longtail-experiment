export interface NotificationApiErrorEnvelope {
  error: {
    code: string;
    message: string;
  };
}

export type NotificationDirection = "up" | "down";
export type NotificationChannel = "in_app";
export type NotificationDeliveryStatus = "queued" | "delivered" | "failed" | "suppressed";
export type NotificationProcessingContext = "incremental" | "historical_reprocessing";
export type NotificationVisibilityClassification = "user_visible" | "audit_only";

export interface NotificationListItem {
  notification_id: string;
  event_id: string;
  dataset_id: string;
  title: string;
  body: string;
  previous_direction: NotificationDirection;
  current_direction: NotificationDirection;
  effective_observed_on: string;
  destination_path: string;
  unread: boolean;
  read_at: string | null;
  delivered_at: string;
  channel: NotificationChannel;
  delivery_status: NotificationDeliveryStatus;
  processing_context: NotificationProcessingContext;
  visibility_classification: NotificationVisibilityClassification;
}

export interface NotificationPaginationInfo {
  page_size: number;
  has_more: boolean;
  next_cursor: string | null;
}

export interface NotificationListResponse {
  items: NotificationListItem[];
  pagination: NotificationPaginationInfo;
}

export interface NotificationSummaryResponse {
  unread_count: number;
  last_notification_at: string | null;
  generated_at: string;
}

export interface MarkReadResponse {
  notification_id: string;
  updated: boolean;
  unread_count: number;
}

export interface MarkUnreadResponse {
  notification_id: string;
  updated: boolean;
  unread_count: number;
}

export interface MarkAllReadResponse {
  updated_count: number;
  unread_count: number;
}

export interface DatasetSubscriptionItem {
  dataset_id: string;
  subscribed_at: string;
  unsubscribed_at: string | null;
}

export interface SubscriptionListResponse {
  items: DatasetSubscriptionItem[];
}

export interface CreateSubscriptionRequest {
  dataset_id: string;
}

export interface SubscriptionResponse {
  dataset_id: string;
  subscribed_at: string;
  created: boolean;
}

export interface DeleteSubscriptionResponse {
  dataset_id: string;
  removed: boolean;
}
