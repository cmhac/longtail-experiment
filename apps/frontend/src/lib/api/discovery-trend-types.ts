export interface TrendTooltipPayload {
  headline: string;
  detail: string;
}

export interface TrendVisualizationSpan {
  start_period: string;
  end_period: string;
  direction: "up" | "down";
  trend_label: string;
  tooltip: TrendTooltipPayload;
}

export interface TrendFeedItem {
  item_type: "trend_event";
  dataset_id: string;
  source: { id: string; name: string };
  title: string;
  direction: "up" | "down";
  strength: string;
  start_period: string;
  latest_update_at: string;
  action_links: {
    view_table_href: string;
    download_csv_href: string;
  };
}
