import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import TopicNotFoundPage from "../src/app/topics/[topicId]/not-found";
import TopicDetailPage from "../src/app/topics/[topicId]/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { buildTopicDetailFixture } from "./fixtures/metadata-discovery-fixtures";
import { renderMarkup } from "./test-utils";

const notFoundMock = vi.fn(() => {
  throw new Error("NOT_FOUND");
});

vi.mock("next/navigation", () => ({
  notFound: () => notFoundMock(),
}));

afterEach(() => {
  notFoundMock.mockClear();
});

describe("topic detail page", () => {
  it("renders topic context and only matching datasets", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchTopicDetail")
      .mockResolvedValue(buildTopicDetailFixture());

    const element = await TopicDetailPage({
      params: Promise.resolve({ topicId: "inflation" }),
    });
    const markup = renderMarkup(element);

    expect(detailSpy).toHaveBeenCalledWith("inflation", { page: 1 });
    expect(markup).toContain("inflation");
    expect(markup).toContain("1 total datasets");
    expect(markup).toContain('data-testid="topic-detail-page"');
    expect(markup).toContain('data-testid="topic-detail-header"');
    expect(markup).toContain("page-header-wrapper");
    expect(markup).toContain('href="/datasets/CPIAUCSL"');
    expect(markup).toContain('data-testid="discovery-feed-list-wrapper"');
  });

  it("renders explicit no-datasets state for valid topics with no datasets", async () => {
    vi.spyOn(discoveryClient, "fetchTopicDetail").mockResolvedValue({
      topic: { id: "inflation", label: "inflation", dataset_count: 0 },
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "title_asc,dataset_id_asc",
    });

    const element = await TopicDetailPage({ params: Promise.resolve({ topicId: "inflation" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("No datasets are currently available for this topic.");
  });

  it("renders generic error state for non-404 topic fetch failures", async () => {
    vi.spyOn(discoveryClient, "fetchTopicDetail").mockRejectedValue(new Error("down"));

    const element = await TopicDetailPage({ params: Promise.resolve({ topicId: "inflation" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
  });

  it("calls notFound for 404-like topic errors", async () => {
    vi.spyOn(discoveryClient, "fetchTopicDetail").mockRejectedValue({ status: 404 });

    await expect(
      TopicDetailPage({ params: Promise.resolve({ topicId: "unknown-topic" }) }),
    ).rejects.toThrow("NOT_FOUND");
    expect(notFoundMock).toHaveBeenCalledTimes(1);
  });

  it("always starts topic detail from page one", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchTopicDetail")
      .mockResolvedValue(buildTopicDetailFixture());

    await TopicDetailPage({ params: Promise.resolve({ topicId: "inflation" }) });

    expect(detailSpy).toHaveBeenCalledWith("inflation", { page: 1 });
  });

  it("boots topic detail from first page only", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchTopicDetail")
      .mockResolvedValue(buildTopicDetailFixture());

    const element = await TopicDetailPage({ params: Promise.resolve({ topicId: "inflation" }) });
    const markup = renderMarkup(element);

    expect(detailSpy).toHaveBeenCalledTimes(1);
    expect(markup).not.toContain('data-testid="infinite-scroll-sentinel"');
  });

  it("renders the topic not-found route inside the shared shell", () => {
    const markup = renderMarkup(<TopicNotFoundPage />);

    expect(markup).toContain('data-testid="site-shell"');
    expect(markup).toContain("Topic not found");
    expect(markup).toContain('href="/datasets"');
  });
});
