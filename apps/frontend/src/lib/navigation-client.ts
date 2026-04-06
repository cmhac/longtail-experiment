export const navigateTo = (path: string): void => {
  if (typeof window === "undefined") {
    return;
  }

  window.location.assign(path);
};
