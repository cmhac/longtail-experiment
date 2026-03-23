import type {
  FurnitureAdapterComponent,
  FurnitureAdapterRegistry,
  FurnitureSlotDefinition,
  FurnitureSlotName,
} from "../contracts";

export const resolveAdapterForSlot = (
  registry: FurnitureAdapterRegistry,
  slotName: FurnitureSlotName,
): FurnitureAdapterComponent => {
  const adapter = registry[slotName];
  if (!adapter) {
    throw new Error(`Missing adapter for slot: ${slotName}`);
  }
  return adapter;
};

export const resolveSlotAdapters = (
  definitions: readonly FurnitureSlotDefinition[],
  registry: FurnitureAdapterRegistry,
): Array<{ slot: FurnitureSlotDefinition; Adapter: FurnitureAdapterComponent }> => {
  return definitions
    .slice()
    .sort((left, right) => left.order - right.order)
    .map((slot) => ({
      slot,
      Adapter: resolveAdapterForSlot(registry, slot.slotName),
    }));
};
