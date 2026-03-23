import React from "react";
import type { JSX } from "react";
import { renderToStaticMarkup } from "react-dom/server";

export const renderMarkup = (element: JSX.Element): string => {
  return renderToStaticMarkup(element);
};
