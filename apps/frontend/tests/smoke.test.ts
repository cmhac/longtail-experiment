import { describe, expect, it } from "vitest";
import { frontendHealthMessage } from "../src/main";

describe("frontend placeholder smoke", () => {
  it("returns frontend-ok", () => {
    expect(frontendHealthMessage()).toBe("frontend-ok");
  });
});
