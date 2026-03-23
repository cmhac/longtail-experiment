"use client";

import { Card } from "@heroui/react";
import React from "react";
import type { JSX } from "react";
import { SHELL_REGION_CLASS_NAMES } from "../theme/monochrome-theme";

export const SITE_HEADER_VARIANT = "light";

export const SiteHeader = (): JSX.Element => {
  return (
    <header
      className={SHELL_REGION_CLASS_NAMES.header}
      data-shell-region="header"
      data-testid="shell-header"
    >
      <Card>
        <Card.Content>
          <p className="shell-eyebrow">Longtail Experiment</p>
          <h1 className="shell-title">Minimal Site Shell</h1>
        </Card.Content>
      </Card>
    </header>
  );
};
