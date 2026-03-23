import type { FurnitureAdapterRegistry } from "../contracts";
import { AdsSubscriptionPlaceholder } from "../placeholders/ads-subscription-placeholder";
import { FooterPlaceholder } from "../placeholders/footer-placeholder";
import { ScriptsAnalyticsPlaceholder } from "../placeholders/scripts-analytics-placeholder";
import { SecondaryNavigationPlaceholder } from "../placeholders/secondary-navigation-placeholder";
import { TopNavigationPlaceholder } from "../placeholders/top-navigation-placeholder";

export const createDefaultFurnitureRegistry = (): FurnitureAdapterRegistry => {
  return {
    "top-navigation": TopNavigationPlaceholder,
    "secondary-navigation": SecondaryNavigationPlaceholder,
    "scripts-analytics": ScriptsAnalyticsPlaceholder,
    "ads-subscription": AdsSubscriptionPlaceholder,
    footer: FooterPlaceholder,
  };
};
