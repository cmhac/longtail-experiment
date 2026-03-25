import React from "react";
import type { JSX } from "react";
import { renderToStaticMarkup } from "react-dom/server";

export const renderMarkup = (element: JSX.Element): string => {
  return renderToStaticMarkup(element);
};

export const expectInOrder = (markup: string, orderedText: string[]): void => {
  let cursor = -1;
  for (const token of orderedText) {
    const nextIndex = markup.indexOf(token, cursor + 1);
    if (nextIndex === -1) {
      throw new Error(`Expected to find token '${token}' after index ${cursor}`);
    }
    cursor = nextIndex;
  }
};
