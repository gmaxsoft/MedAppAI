import { describe, expect, it } from "vitest";

import { cn } from "./utils";

describe("cn", () => {
  it("scala klasy i ignoruje fałszywe wartości", () => {
    expect(cn("px-2", false && "hidden", "py-1")).toBe("px-2 py-1");
  });
});
