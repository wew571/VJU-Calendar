import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CourseEditDrawer from "./CourseEditDrawer";

const app = vi.hoisted(() => ({
  addManualCourse: vi.fn(),
  updateManualCourse: vi.fn(),
}));

vi.mock("../../context/AppDataContext", () => ({
  useAppData: () => ({ loading: false, ...app }),
}));

describe("CourseEditDrawer", () => {
  beforeEach(() => vi.clearAllMocks());

  it("dung cung kich thuoc popup giang vien va bo cac dong mo ta thua", () => {
    render(
      <CourseEditDrawer
        course={{ id: 10, code: "MTH101", name: "Giải tích", credits: 3 }}
        onClose={vi.fn()}
      />,
    );

    const dialog = screen.getByRole("dialog", { name: "Sửa học phần #10" });
    expect(dialog).toHaveClass(
      "teacher-edit-dialog",
      "manual-edit-glass",
      "w-[min(1000px,calc(100vw-2rem))]",
      "h-[min(600px,calc(100dvh-2rem))]",
    );
    expect(screen.queryByText("Chuẩn bị dữ liệu / Học phần")).not.toBeInTheDocument();
    expect(screen.queryByText("Sửa ở đây áp dụng cho tất cả lớp thuộc học phần này.")).not.toBeInTheDocument();
  });

  it("giu nguyen luong sua va luu hoc phan", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    app.updateManualCourse.mockResolvedValue({});
    render(
      <CourseEditDrawer
        course={{ id: 10, code: "MTH101", name: "Giải tích", credits: 3 }}
        onClose={onClose}
      />,
    );

    const name = screen.getByRole("textbox", { name: /Tên học phần/ });
    await user.clear(name);
    await user.type(name, "Giải tích nâng cao");
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    await waitFor(() => expect(app.updateManualCourse).toHaveBeenCalledWith(10, {
      code: "MTH101",
      name: "Giải tích nâng cao",
      credits: 3,
    }));
    expect(onClose).toHaveBeenCalled();
  });

  it("giữ và lưu được mức tín chỉ cũ ngoài danh sách", async () => {
    const user = userEvent.setup();
    app.updateManualCourse.mockResolvedValue({});
    render(
      <CourseEditDrawer
        course={{ id: 10, code: "MTH101", name: "Giải tích", credits: 7 }}
        onClose={vi.fn()}
      />,
    );

    const credits = screen.getByRole("combobox", { name: "Số tín chỉ" });
    expect(credits).toHaveValue("7");
    expect(within(credits).getByRole("option", { name: "7" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Lưu" }));
    await waitFor(() => expect(app.updateManualCourse).toHaveBeenCalledWith(10, expect.objectContaining({ credits: 7 })));
  });

  it("chi cho chon so tin chi tu danh sach co dinh", async () => {
    const user = userEvent.setup();
    app.updateManualCourse.mockResolvedValue({});
    render(
      <CourseEditDrawer
        course={{ id: 10, code: "MTH101", name: "Giải tích", credits: 3 }}
        onClose={vi.fn()}
      />,
    );

    const credits = screen.getByRole("combobox", { name: "Số tín chỉ" });
    expect(credits).toHaveValue("3");
    expect(credits.parentElement).toHaveClass("w-full");
    expect(within(credits).getAllByRole("option").map((o) => o.value)).toEqual(
      ["", "1", "2", "3", "4", "5", "10", "12"],
    );

    await user.selectOptions(credits, "10");
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    await waitFor(() => expect(app.updateManualCourse).toHaveBeenCalledWith(10, {
      code: "MTH101",
      name: "Giải tích",
      credits: 10,
    }));
  });
});
