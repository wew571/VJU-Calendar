import { describe, expect, it } from "vitest";
import { getAllowedGroups } from "@/constants/nav";
import { clampPageForRole, clampSubForRole, ROLE_DEFINITIONS } from "@/constants/roles";

describe("role navigation and permissions", () => {
  it("keeps schedule access limited to GĐCT and Trợ lý khoa", () => {
    expect(ROLE_DEFINITIONS.gdct.canSchedule).toBe(true);
    expect(ROLE_DEFINITIONS.assistant.canSchedule).toBe(true);
    expect(ROLE_DEFINITIONS.dpct.canSchedule).toBe(false);
    expect(clampPageForRole("schedule", "dpct")).toBe("data");
  });

  it("does not grant unassigned course-data editing to any business role", () => {
    for (const role of ["gdct", "dpct", "assistant", "resident"]) {
      const groups = getAllowedGroups(role);
      expect(groups.some((group) => group.key === "manual")).toBe(false);
      expect(groups.find((group) => group.key === "data").children.map(({ key }) => key))
        .toEqual(["availability"]);
      expect(clampSubForRole("data", "hours", role)).toBe("availability");
    }
  });

  it("limits the resident profile to availability declaration", () => {
    expect(ROLE_DEFINITIONS.resident.canDeclareOwnAvailability).toBe(true);
    expect(ROLE_DEFINITIONS.resident.canManageGuests).toBe(false);
    expect(ROLE_DEFINITIONS.resident.canSchedule).toBe(false);
    expect(getAllowedGroups("resident").map(({ key }) => key)).toEqual(["data"]);
  });
});
