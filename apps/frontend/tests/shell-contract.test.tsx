import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { createDefaultFurnitureRegistry } from "../src/furniture/adapters/registry";
import { resolveSlotAdapters } from "../src/furniture/adapters/slot-adapter-mapper";
import type { FurnitureAdapterRegistry } from "../src/furniture/contracts";
import { AppShell } from "../src/shell/app-shell";
import { REQUIRED_FURNITURE_SLOTS } from "../src/shell/slots/slot-definitions";

describe("frontend furniture contracts", () => {
  it("keeps five required slot definitions", () => {
    expect(REQUIRED_FURNITURE_SLOTS).toHaveLength(5);
    expect(REQUIRED_FURNITURE_SLOTS.map((slot) => slot.slotName)).toEqual([
      "top-navigation",
      "secondary-navigation",
      "scripts-analytics",
      "ads-subscription",
      "footer",
    ]);
  });

  it("resolves adapters for each required slot", () => {
    const registry = createDefaultFurnitureRegistry();
    const mappings = resolveSlotAdapters(REQUIRED_FURNITURE_SLOTS, registry);

    expect(mappings).toHaveLength(5);
    for (const mapping of mappings) {
      expect(typeof mapping.Adapter).toBe("function");
    }
  });

  it("rejects a registry missing a required slot", () => {
    const partialRegistry = {
      "top-navigation": createDefaultFurnitureRegistry()["top-navigation"],
    } as unknown as FurnitureAdapterRegistry;

    expect(() => resolveSlotAdapters(REQUIRED_FURNITURE_SLOTS, partialRegistry)).toThrow(
      "Missing adapter for slot",
    );
  });

  it("supports contract-compliant adapter swaps", () => {
    const defaultRegistry = createDefaultFurnitureRegistry();
    const swappedRegistry: FurnitureAdapterRegistry = {
      ...defaultRegistry,
      "top-navigation": ({ slot }) => <div data-testid={slot.testId}>Swapped top slot</div>,
    };

    const markup = renderToStaticMarkup(<AppShell adapterRegistry={swappedRegistry} />);
    expect(markup).toContain("Swapped top slot");
    expect(markup).toContain('data-testid="footer-slot"');
  });

  it("renders an intentionally empty main region", () => {
    const markup = renderToStaticMarkup(<AppShell />);
    expect(markup).toContain('data-testid="main-content-region"');
    expect(markup).toContain('<main class="main-region" data-testid="main-content-region"></main>');
  });
});
