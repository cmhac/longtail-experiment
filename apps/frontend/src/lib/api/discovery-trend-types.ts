export interface TrendTooltipPayload {
  title: string;
  start_period: string;
  direction: "up" | "down" | "flat";
  strength: string;
  end_period?: string | null;
  seasonality_classification?: string;
}

export interface TrendVisualizationSpan {
  span_id: string;
  start_x: string;
  end_x: string;
  direction: "up" | "down" | "flat";
  color_token: string;
  pattern_token: string;
  direction_icon: string;
  tooltip: TrendTooltipPayload;
}

export interface TrendFeedItem {
  item_type: "trend_event";
  event_timestamp: string;
  dataset_id: string;
  direction: "up" | "down" | "flat";
  strength: string;
  start_period: string;
  end_period?: string | null;
  is_ongoing: boolean;
}
