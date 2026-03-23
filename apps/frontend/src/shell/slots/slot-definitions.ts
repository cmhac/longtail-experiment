import type { FurnitureSlotDefinition } from "../../furniture/contracts";

export const REQUIRED_FURNITURE_SLOTS: readonly FurnitureSlotDefinition[] = [
  {
    slotName: "top-navigation",
    order: 1,
    testId: "top-navigation-slot",
    label: "Top navigation slot",
  },
  {
    slotName: "secondary-navigation",
    order: 2,
    testId: "secondary-navigation-slot",
    label: "Secondary navigation slot",
  },
  {
    slotName: "scripts-analytics",
    order: 3,
    testId: "scripts-analytics-slot",
    label: "Scripts and analytics slot",
  },
  {
    slotName: "ads-subscription",
    order: 4,
    testId: "ads-subscription-slot",
    label: "Ads and subscription slot",
  },
  {
    slotName: "footer",
    order: 5,
    testId: "footer-slot",
    label: "Footer slot",
  },
] as const;
