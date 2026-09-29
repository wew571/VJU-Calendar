import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SectionEditDrawer from "./SectionEditDrawer";

const app = vi.hoisted(() => ({
  updateManualSection: vi.fn(),
  addManualSection: vi.fn(),
  addManualTeacher: vi.fn(),
  deleteManualSection: vi.fn(),
  doBoQua: vi.fn(),
}));

vi.mock("../../context/AppDataContext", () => ({
  useAppData: () => ({ loading: false, ...app }),
}));

const data = {
  numDays: 7,
  slotsPerDay: 12,
  teachers: [
    { id: 1, name: "GV cơ hữu", type: "RESIDENT" },
    { id: 2, name: "GV thỉnh giảng", type: "GUEST" },
  ],
  courses: [
    { id: 10, code: "MTH101", name: "Giải tích" },
    { id: 11, code: "MTH102", name: "Đại số tuyến tính" },
    { id: 12, code: "PHY101", name: "Vật lý đại cương" },
  ],
};

function makeSection(overrides = {}) {
  return {
    sectionId: 20,
    teacherIds: [1],
    courseId: 10,
    classCode: "MTH101-1",
    programName: "BCSE",
    ltCredits: 3,
    thCredits: 0,
    cohort: "K68",
    expectedStudents: 30,
    duration: 3,
    timeAssumed: false,
    day: 0,
    periodStart: 1,
    periodEnd: 3,
    location: "Hòa Lạc",
    teachingMode: "Trực tiếp",
    ...overrides,
  };
}

describe("SectionEditDrawer", () => {
  beforeAll(() => {
    globalThis.ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  });
  beforeEach(() => vi.clearAllMocks());

  it("dung popup 1500x750 ba cot, dat Thoi gian o cot cuoi va khong them nhanh hoc phan", () => {
    render(<SectionEditDrawer data={data} section={makeSection()} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog", { name: "Sửa lớp MTH101-1" });
    expect(dialog).toHaveClass("w-[min(1500px,calc(100vw-2rem))]", "h-[min(750px,calc(100dvh-2rem))]");
    const body = dialog.querySelector(".grid-cols-1");
    expect(body).toHaveClass("min-[1100px]:grid-cols-3");
    expect(body.children).toHaveLength(3);
    expect(screen.getByRole("heading", { name: "Thời gian" }).closest("section").parentElement).toBe(body.children[2]);
    expect(screen.queryByRole("button", { name: "Học phần mới" })).not.toBeInTheDocument();
    expect(screen.queryByText(/Hệ thống tạm suy ra vì file không ghi giờ/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Chuẩn bị dữ liệu/)).not.toBeInTheDocument();
    expect(screen.queryByText(/MỌI NGƯỜI VAI TRÒ NGANG NHAU/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Chỉ để đối chiếu/)).not.toBeInTheDocument();
  });

  it("loc danh sach hoc phan theo ma hoac ten khi nguoi dung nhap", async () => {
    const user = userEvent.setup();
    render(<SectionEditDrawer data={data} section={makeSection()} onClose={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: /Học phần/ }));
    const search = screen.getByPlaceholderText("Tìm mã hoặc tên học phần…");
    await user.type(search, "đại số");

    const menu = screen.getByRole("menu");
    expect(within(menu).getByText("MTH102 — Đại số tuyến tính")).toBeInTheDocument();
    expect(within(menu).queryByText("MTH101 — Giải tích")).not.toBeInTheDocument();
    expect(within(menu).queryByText("PHY101 — Vật lý đại cương")).not.toBeInTheDocument();

    await user.click(within(menu).getByText("MTH102 — Đại số tuyến tính"));
    expect(screen.getByRole("button", { name: /Học phần/ })).toHaveTextContent("MTH102 — Đại số tuyến tính");
  });

  it("xoa gio dang chon khi doi so tiet lam sai do dai", async () => {
    const user = userEvent.setup();
    render(<SectionEditDrawer data={data} section={makeSection()} onClose={vi.fn()} />);

    const duration = screen.getByRole("spinbutton", { name: /Số tiết \/ buổi/ });
    await user.clear(duration);
    await user.type(duration, "2");

    expect(screen.queryAllByRole("button", { pressed: true })).toHaveLength(0);
    expect(screen.getByText("Bấm một ô để chọn đủ 2 tiết liên tiếp trong cùng ngày.")).toBeInTheDocument();
  });

  it("xoa gio Thu 7 khi doi nhom tu thinh giang sang co huu", async () => {
    const user = userEvent.setup();
    render(
      <SectionEditDrawer
        data={data}
        section={makeSection({ teacherIds: [2], day: 5, periodStart: 1, periodEnd: 3 })}
        onClose={vi.fn()}
      />,
    );

    const teacherSelect = screen.getAllByRole("combobox").find((select) => select.value === "2");
    await user.selectOptions(teacherSelect, "1");

    expect(screen.queryAllByRole("button", { pressed: true })).toHaveLength(0);
    expect(screen.getByText("Bấm một ô để chọn đủ 3 tiết liên tiếp trong cùng ngày.")).toBeInTheDocument();
  });

  it("khoa bang gio lop da chot va luu nguyen dai gio", async () => {
    const user = userEvent.setup();
    app.updateManualSection.mockResolvedValue({});
    render(
      <SectionEditDrawer
        data={data}
        section={makeSection({ sectionChot: { by: "Giáo vụ", at: "2026-09-29T10:00:00" } })}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByRole("checkbox", { name: "Để hệ thống tự xếp giờ" })).toBeDisabled();
    expect(screen.getAllByRole("button", { pressed: true })).toHaveLength(3);
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    await waitFor(() => expect(app.updateManualSection).toHaveBeenCalled());
    expect(app.updateManualSection.mock.calls[0][1]).toMatchObject({
      day: 0,
      periodStart: 1,
      periodEnd: 3,
    });
  });
});
