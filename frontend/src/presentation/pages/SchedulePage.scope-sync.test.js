import { describe, expect, it } from "vitest";
import { buildScheduleView, DEFAULT_FILTER } from "../../adapters/scheduleView";
import { boLocTheoPhamVi, boLocXemDeKhoiPhuc } from "./SchedulePage";

const classes = [
  { sectionId: 1, programParts: ["BCSE"], cohortParts: ["VJU2025"] },
  { sectionId: 2, programParts: ["BCSE"], cohortParts: ["VJU2024"] },
  { sectionId: 3, programParts: ["BCSE"], cohortParts: ["VJU2023"] },
  { sectionId: 4, programParts: ["FTH"], cohortParts: ["VJU2025"] },
];

const lessons = classes.map((section, index) => ({
  id: section.sectionId,
  day: 0,
  period: index,
  slot: index,
  duration: 1,
  teacherId: index + 1,
  teacherType: "GUEST",
}));

describe("SchedulePage - đồng bộ phạm vi xếp với lưới", () => {
  it("bật xem đúng phạm vi gần nhất khi mở hoặc thay đổi Xếp cho", () => {
    expect(boLocTheoPhamVi({ programs: ["BCSE"], cohorts: ["VJU2025", "VJU2024"] })).toEqual({
      scope: "all",
      scopeValue: "",
      khoa: "",
      guest: true,
      resident: true,
      search: "",
      onlyProblems: false,
      chiXemPhamVi: true,
    });
    expect(boLocTheoPhamVi(null).chiXemPhamVi).toBe(false);
    expect(boLocXemDeKhoiPhuc(DEFAULT_FILTER)).toEqual(DEFAULT_FILTER);
    expect(boLocXemDeKhoiPhuc({ ...DEFAULT_FILTER, scope: "program", scopeValue: "FTH", chiXemPhamVi: true }))
      .toMatchObject({ scope: "program", scopeValue: "FTH", chiXemPhamVi: false });
  });

  it("hien dong thoi cac lop BCSE cua hai khoa da chon", () => {
    const phamVi = { programs: ["BCSE"], cohorts: ["VJU2025", "VJU2024"] };
    const view = buildScheduleView({
      data: { classes, numDays: 7, slotsPerDay: 12 },
      guestResult: { lessons },
      residentResult: null,
      inbox: { items: [] },
      filter: { ...DEFAULT_FILTER, ...boLocTheoPhamVi(phamVi) },
      phamVi,
    });

    expect(view.lessons.map((lesson) => lesson.id)).toEqual([1, 2]);
  });
});
