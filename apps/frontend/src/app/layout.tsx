import Script from "next/script";
import React from "react";
import type { JSX, ReactNode } from "react";
import "./globals.css";

interface RootLayoutProps {
  children: ReactNode;
}

const RootLayout = ({ children }: RootLayoutProps): JSX.Element => {
  return (
    <html className="shell-root bg-background text-foreground" lang="en" suppressHydrationWarning>
      <body className="shell-body bg-background text-foreground antialiased">
        <Script id="system-theme-sync" strategy="beforeInteractive">
          {`(() => {
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
})();`}
        </Script>
        {children}
      </body>
    </html>
  );
};

export default RootLayout;
