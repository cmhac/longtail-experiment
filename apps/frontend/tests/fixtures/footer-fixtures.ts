import { FOOTER_CONTENT, type FooterContent } from "../../src/shell/footer-content";

export const createFooterFixture = (overrides: Partial<FooterContent> = {}): FooterContent => {
  return {
    ...FOOTER_CONTENT,
    ...overrides,
  };
};
