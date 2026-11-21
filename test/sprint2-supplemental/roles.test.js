import { describe, expect, it } from "vitest";
import { getAllowedGroups, VIEWER_ALLOWED_KEYS } from "@/constants/nav";

describe("Sprint 2 supplemental navigation boundaries", () => {
  it("keeps the viewer role limited to the documented read-only pages", () => {
    expect(VIEWER_ALLOWED_KEYS).toEqual(["schedule", "history", "guide"]);
    expect(getAllowedGroups("viewer").map(({ key }) => key)).toEqual(["history"]);
  });

  it("keeps staff navigation available in the current implementation", () => {
    expect(getAllowedGroups("staff").map(({ key }) => key)).toEqual(["manual", "data", "history"]);
  });
});
