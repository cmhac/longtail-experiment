"use client";

import { Card } from "@heroui/react";
import React from "react";
import type { JSX } from "react";
import { SHELL_REGION_CLASS_NAMES } from "../theme/monochrome-theme";

export const CONTENT_PLACEHOLDER_VARIANT = "flat";

export const ContentPlaceholder = (): JSX.Element => {
  return (
    <main
      className={SHELL_REGION_CLASS_NAMES.main}
      data-shell-region="main-placeholder"
      data-testid="shell-main-placeholder"
    >
      <Card>
        <Card.Content>
          <h2 className="shell-subtitle">Content Placeholder</h2>
          <p className="shell-copy">Feature content will appear here soon.</p>
        </Card.Content>
      </Card>
    </main>
  );
};
