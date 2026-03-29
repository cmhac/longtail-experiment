import React from "react";
import type { JSX, ReactNode } from "react";
import {
  createRootDocumentAttributes,
  resolveInitialThemePreference,
} from "../theme/theme-preference";
import "./globals.css";

interface RootLayoutProps {
  children: ReactNode;
}

const RootLayout = ({ children }: RootLayoutProps): JSX.Element => {
  const rootAttributes = createRootDocumentAttributes(resolveInitialThemePreference());

  return (
    <html
      className={rootAttributes.className}
      data-theme-preference={rootAttributes.dataThemePreference}
      lang="en"
      style={rootAttributes.style}
    >
      <body className="shell-body bg-background text-foreground antialiased">{children}</body>
    </html>
  );
};

export default RootLayout;
