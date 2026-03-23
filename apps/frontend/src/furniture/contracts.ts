import type { ComponentType } from "react";

export const REQUIRED_SLOT_NAMES = [
  "top-navigation",
  "secondary-navigation",
  "footer",
  "scripts-analytics",
  "ads-subscription",
] as const;

export type FurnitureSlotName = (typeof REQUIRED_SLOT_NAMES)[number];

export const PROCESS_HOOK_NAMES = ["env_bootstrap", "data_bootstrap", "publish_extension"] as const;

export type SlotLifecycleHook = (typeof PROCESS_HOOK_NAMES)[number];

export interface FurnitureSlotDefinition {
  slotName: FurnitureSlotName;
  order: number;
  testId: string;
  label: string;
}

export interface FurnitureAdapterProps {
  slot: FurnitureSlotDefinition;
}

export type FurnitureAdapterComponent = ComponentType<FurnitureAdapterProps>;

export type FurnitureAdapterRegistry = Record<FurnitureSlotName, FurnitureAdapterComponent>;
