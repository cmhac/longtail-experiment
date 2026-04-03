import React from "react";
import type { JSX, ReactNode } from "react";
import "./globals.css";

const SYSTEM_THEME_BOOTSTRAP_SCRIPT = `(() => {
  const root = document.documentElement;
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const applyTheme = (isDark) => {
    root.classList.toggle('dark', isDark);
    root.setAttribute('data-theme', isDark ? 'dark' : 'light');
  };

  applyTheme(mediaQuery.matches);

  const handleChange = (event) => applyTheme(event.matches);
  if (typeof mediaQuery.addEventListener === 'function') {
    mediaQuery.addEventListener('change', handleChange);
  } else {
    mediaQuery.addListener(handleChange);
  }
})();`;

interface RootLayoutProps {
  children: ReactNode;
}

const RootLayout = ({ children }: RootLayoutProps): JSX.Element => {
  return (
    <html className="shell-root bg-background text-foreground" lang="en" suppressHydrationWarning>
      <head>
        <script id="system-theme-sync">{SYSTEM_THEME_BOOTSTRAP_SCRIPT}</script>
      </head>
      <body className="shell-body bg-background text-foreground antialiased">{children}</body>
    </html>
  );
};

export default RootLayout;
