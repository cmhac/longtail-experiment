export type TrendDirection = "up" | "down";

interface TrendDirectionToken {
  ariaLabel: string;
  icon: string;
  overlayClassName: string;
}

export const TREND_DIRECTION_TOKENS: Record<TrendDirection, TrendDirectionToken> = {
  up: {
    ariaLabel: "Upward trend",
    icon: "^",
    overlayClassName:
      "border-emerald-500/70 bg-[repeating-linear-gradient(135deg,rgba(16,185,129,0.24)_0_8px,rgba(16,185,129,0.38)_8px_14px)] text-emerald-900",
  },
  down: {
    ariaLabel: "Downward trend",
    icon: "v",
    overlayClassName:
      "border-rose-500/70 bg-[repeating-linear-gradient(45deg,rgba(244,63,94,0.22)_0_8px,rgba(244,63,94,0.36)_8px_14px)] text-rose-900",
  },
};
