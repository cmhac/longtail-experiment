import React from "react";
import { describe, expect, it } from "vitest";
import {
  PageHeaderKicker,
  PageHeaderSubtitle,
  PageHeaderTitle,
  PageHeaderWrapper,
} from "../src/components/discovery/PageHeader";
import { renderMarkup } from "./test-utils";

describe("PageHeader primitives", () => {
  it("renders wrapper with border and custom children", () => {
    const markup = renderMarkup(
      <PageHeaderWrapper testId="test-page-header">
        <div>Primary block</div>
        <div data-testid="header-actions">Actions block</div>
      </PageHeaderWrapper>,
    );

    expect(markup).toContain('data-testid="test-page-header"');
    expect(markup).toContain("page-header-wrapper");
    expect(markup).toContain("border-b");
    expect(markup).toContain("Primary block");
    expect(markup).toContain('data-testid="header-actions"');
  });

  it("renders kicker and subtitle text variants", () => {
    const markup = renderMarkup(
      <PageHeaderWrapper>
        <PageHeaderKicker testId="header-kicker">Data Source</PageHeaderKicker>
        <PageHeaderSubtitle testId="header-subtitle">Descriptive subtitle text.</PageHeaderSubtitle>
      </PageHeaderWrapper>,
    );

    expect(markup).toContain('data-testid="header-kicker"');
    expect(markup).toContain('data-testid="header-subtitle"');
    expect(markup).toContain("Data Source");
    expect(markup).toContain("Descriptive subtitle text.");
    expect(markup).toContain("page-header-kicker");
    expect(markup).toContain("page-header-subtitle");
  });

  it("renders default and hero title sizes", () => {
    const defaultMarkup = renderMarkup(
      <PageHeaderTitle testId="title-default">Datasets</PageHeaderTitle>,
    );
    const heroMarkup = renderMarkup(
      <PageHeaderTitle size="hero" testId="title-hero">
        Retail Gasoline Prices
      </PageHeaderTitle>,
    );

    expect(defaultMarkup).toContain('data-testid="title-default"');
    expect(defaultMarkup).toContain("page-header-title");
    expect(defaultMarkup).toContain("text-[clamp(2rem,4vw,2.8rem)]");

    expect(heroMarkup).toContain('data-testid="title-hero"');
    expect(heroMarkup).toContain("text-[clamp(2rem,3.9vw,3.45rem)]");
  });
});
