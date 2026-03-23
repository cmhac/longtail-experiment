import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import RootLayout from "../src/app/layout";
import { runDataBootstrap } from "../src/server/hooks/data-bootstrap";
import { runEnvBootstrap } from "../src/server/hooks/env-bootstrap";
import { runPublishExtension } from "../src/server/hooks/publish-extension";
import { SHELL_REGION_ORDER } from "../src/shell/shell-regions";

describe("foundation contracts", () => {
  it("renders root layout shell document", () => {
    const markup = renderToStaticMarkup(
      <RootLayout>
        <div id="child" />
      </RootLayout>,
    );

    expect(markup).toContain("<html");
    expect(markup).toContain('lang="en"');
    expect(markup).toContain('<body class="shell-body">');
    expect(markup).toContain('id="child"');
  });

  it("exports required shell region contract constants", () => {
    expect(SHELL_REGION_ORDER).toEqual(["header", "main-placeholder", "footer"]);
  });

  it("executes stub lifecycle hooks without side effects", () => {
    expect(runEnvBootstrap()).toEqual({ status: "stubbed", hook: "env_bootstrap" });
    expect(runDataBootstrap()).toEqual({ status: "stubbed", hook: "data_bootstrap" });
    expect(runPublishExtension()).toEqual({ status: "stubbed", hook: "publish_extension" });
  });
});
