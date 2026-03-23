import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import RootLayout from "../src/app/layout";
import { PROCESS_HOOK_NAMES, REQUIRED_SLOT_NAMES } from "../src/furniture/contracts";
import { runDataBootstrap } from "../src/server/hooks/data-bootstrap";
import { runEnvBootstrap } from "../src/server/hooks/env-bootstrap";
import { runPublishExtension } from "../src/server/hooks/publish-extension";

describe("foundation contracts", () => {
  it("renders root layout shell document", () => {
    const markup = renderToStaticMarkup(
      <RootLayout>
        <div id="child" />
      </RootLayout>,
    );

    expect(markup).toContain('<html lang="en"');
    expect(markup).toContain("<body>");
    expect(markup).toContain('id="child"');
  });

  it("exports required slot and hook contract constants", () => {
    expect(REQUIRED_SLOT_NAMES).toHaveLength(5);
    expect(REQUIRED_SLOT_NAMES).toContain("top-navigation");
    expect(PROCESS_HOOK_NAMES).toEqual(["env_bootstrap", "data_bootstrap", "publish_extension"]);
  });

  it("executes stub lifecycle hooks without side effects", () => {
    expect(runEnvBootstrap()).toEqual({ status: "stubbed", hook: "env_bootstrap" });
    expect(runDataBootstrap()).toEqual({ status: "stubbed", hook: "data_bootstrap" });
    expect(runPublishExtension()).toEqual({ status: "stubbed", hook: "publish_extension" });
  });
});
