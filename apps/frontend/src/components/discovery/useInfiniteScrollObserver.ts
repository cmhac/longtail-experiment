"use client";

import React from "react";

interface UseInfiniteScrollObserverOptions {
  enabled: boolean;
  onIntersect: () => void;
  rootRef?: React.RefObject<HTMLElement | null>;
  rootMargin?: string;
  threshold?: number;
}

export const useInfiniteScrollObserver = ({
  enabled,
  onIntersect,
  rootRef,
  rootMargin = "0px",
  threshold = 0,
}: UseInfiniteScrollObserverOptions): React.RefObject<HTMLDivElement | null> => {
  const sentinelRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (!enabled) {
      return;
    }

    const sentinel = sentinelRef.current;
    if (!sentinel) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (!entry?.isIntersecting) {
          return;
        }

        onIntersect();
      },
      {
        root: rootRef?.current ?? null,
        rootMargin,
        threshold,
      },
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [enabled, onIntersect, rootMargin, rootRef, threshold]);

  return sentinelRef;
};
