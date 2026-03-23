import React from "react";
import type { JSX } from "react";
import { createDefaultFurnitureRegistry } from "../furniture/adapters/registry";
import { resolveSlotAdapters } from "../furniture/adapters/slot-adapter-mapper";
import type { FurnitureAdapterRegistry } from "../furniture/contracts";
import { REQUIRED_FURNITURE_SLOTS } from "./slots/slot-definitions";

interface AppShellProps {
  adapterRegistry?: FurnitureAdapterRegistry;
}

export const AppShell = ({ adapterRegistry }: AppShellProps): JSX.Element => {
  const registry = adapterRegistry ?? createDefaultFurnitureRegistry();
  const slotAdapters = resolveSlotAdapters(REQUIRED_FURNITURE_SLOTS, registry);

  return (
    <div className="app-shell" data-testid="app-shell">
      <header className="shell-band shell-band-primary">
        <h1 className="shell-title">Longtail Frontend Shell</h1>
      </header>
      <div className="shell-layout">
        {slotAdapters.map(({ slot, Adapter }) => (
          <section className="shell-slot" data-slot-name={slot.slotName} key={slot.slotName}>
            <Adapter slot={slot} />
          </section>
        ))}
        <main className="main-region" data-testid="main-content-region" />
      </div>
    </div>
  );
};
