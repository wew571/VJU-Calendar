import { beforeAll, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import SectionTable from "./SectionTable";

function makeRow(overrides = {}) {
  return {
    sectionId: 20,
    courseId: 10,
    courseCode: "MTH101",
    courseName: "Giải tích",
    credits: 3,
    classCode: "MTH101-1",
    duration: 4,
    ltCredits: 3,
    thCredits: 1,
    cohort: "K68",
    programLabel: "BCSE",
    expectedStudents: 30,
    day: 0,
    periodStart: 2,
    periodEnd: 5,
    teachers: [
      { id: 1, title: "PGS.TS", name: "Nguyễn Văn A", org: "VJU", email: "a@example.com", phone: "0901" },
      { id: 2, title: "TS", name: "Trần Thị B", org: "Đơn vị B", email: "b@example.com", phone: "0902", outsideDeclared: true },
    ],
    prevTeacherName: "Giảng viên kỳ trước",
    prevTeacherOrg: "Đơn vị kỳ trước",
    teachingHoursLt: 30,
    teachingHoursTh: 15,
    location: "Hòa Lạc",
    teachingMode: "Trực tiếp",
    language: "Tiếng Việt",
    otherRequirements: "Máy chiếu",
    notes: "Ghi chú riêng",
    status: "ready_fixed",
    scheduleStatus: "scheduled",
    ...overrides,
  };
}

function renderTable(rows, overrides = {}) {
  return render(
    <SectionTable
      rows={rows}
      canEdit
      loading={false}
      tenLop={(row) => row.classCode}
      onOpenSection={() => vi.fn()}
      onOpenCourse={() => vi.fn()}
      onOpenTeacher={() => vi.fn()}
      onChot={vi.fn()}
      onBoChot={() => vi.fn()}
      onBoHocChung={vi.fn()}
      {...overrides}
    />,
  );
}

describe("SectionTable", () => {
  beforeAll(() => {
    globalThis.ResizeObserver = class {
      observe() {}
      disconnect() {}
    };
  });

  it("chi hien 17 cot tom tat va gop hai moc tiet thanh mot dai", () => {
    renderTable([makeRow()]);

    const table = screen.getByRole("table");
    expect(within(table).getByRole("columnheader", { name: "Tiết giảng dạy" })).toBeInTheDocument();
    expect(within(table).getByText("2 - 5")).toBeInTheDocument();
    expect(table.querySelector("thead").rows).toHaveLength(2);
    expect(table.querySelector("tbody .xls-row").cells).toHaveLength(17);

    for (const header of ["Phân bổ TC", "Tiết đầu", "Tiết cuối", "Kỳ trước (để đối chiếu)", "Kỳ này", "Số giờ dạy", "Hình thức", "Ngôn ngữ", "Yêu cầu khác", "Ghi chú"]) {
      expect(within(table).queryByRole("columnheader", { name: header })).not.toBeInTheDocument();
    }
    for (const hiddenValue of ["Giảng viên kỳ trước", "Đơn vị kỳ trước", "VJU", "a@example.com", "0901", "Trực tiếp", "Tiếng Việt", "Máy chiếu", "Ghi chú riêng"]) {
      expect(within(table).queryByText(hiddenValue)).not.toBeInTheDocument();
    }
  });

  it("thong nhat cac o thieu du lieu thanh dau gach", () => {
    renderTable([makeRow({
      day: null,
      periodEnd: null,
      programLabel: null,
      location: "",
      status: null,
      scheduleStatus: null,
    })]);

    const row = screen.getByRole("table").querySelector("tbody .xls-row");
    for (const index of [8, 10, 11, 14, 15, 16]) {
      expect(row.cells[index]).toHaveTextContent("—");
    }
    expect(row).not.toHaveTextContent("2 -");
    expect(row).not.toHaveTextContent("null");
    expect(row).not.toHaveTextContent("undefined");
  });

  it("giu du tung giang vien, canh bao gio lech va mo dung popup", () => {
    const firstTeacher = vi.fn((event) => event.stopPropagation());
    const secondTeacher = vi.fn((event) => event.stopPropagation());
    const onOpenTeacher = vi.fn((id) => (id === 1 ? firstTeacher : secondTeacher));
    renderTable([makeRow()], { onOpenTeacher });

    fireEvent.click(screen.getByRole("button", { name: "Nguyễn Văn A" }));
    fireEvent.click(screen.getByRole("button", { name: "Trần Thị B" }));

    expect(firstTeacher).toHaveBeenCalledOnce();
    expect(secondTeacher).toHaveBeenCalledOnce();
    expect(screen.getByRole("button", { name: "Trần Thị B" })).toHaveClass("xls-gv-venh");
  });

  it("de thong bao bang rong phu du 17 cot", () => {
    renderTable([]);

    expect(screen.getByText("Chưa có lớp nào khớp bộ lọc.")).toHaveAttribute("colspan", "17");
  });
});
