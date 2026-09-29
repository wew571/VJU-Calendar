import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DEFAULT_FILTER } from "../../adapters/scheduleView";
import ScheduleToolbar, { ScheduleActions } from "./ScheduleToolbar";

const view = {
  programs: ["FTH", "BCSE"],
  cohorts: ["VJU2026", "VJU2025"],
  teachers: [{ id: 1, name: "Nguyễn Văn A" }],
  lessons: [{ id: 1 }],
};

describe("ScheduleToolbar", () => {
  it("ưu tiên phạm vi và tìm kiếm, thu gọn các bộ lọc phụ", async () => {
    const user = userEvent.setup();
    const set = vi.fn();
    const { container } = render(
      <ScheduleToolbar
        f={DEFAULT_FILTER}
        set={set}
        view={view}
        mode="grid"
        phamVi={null}
      />,
    );

    expect(screen.getByLabelText("Xem")).toHaveValue("all");
    expect(screen.getByPlaceholderText("Tìm môn, giảng viên, #id")).toBeInTheDocument();
    const details = container.querySelector("details");
    expect(details).not.toHaveAttribute("open");

    await user.click(screen.getByText("Bộ lọc thêm"));
    expect(details).toHaveAttribute("open");
    expect(screen.getByLabelText("Cách tô màu")).toBeInTheDocument();

    await user.click(screen.getByText("Chỉ buổi có vấn đề"));
    expect(set).toHaveBeenCalledWith({ onlyProblems: true });
  });

  it("hiện số bộ lọc phụ đang dùng", () => {
    render(
      <ScheduleToolbar
        f={{ ...DEFAULT_FILTER, resident: false, onlyProblems: true, colorBy: "program" }}
        set={vi.fn()}
        view={view}
        mode="grid"
        phamVi={null}
      />,
    );

    expect(screen.getByText("3")).toBeInTheDocument();
  });
});

describe("ScheduleActions", () => {
  it("giữ thao tác xem cho viewer và ẩn thao tác chỉnh sửa", () => {
    render(
      <ScheduleActions
        data={{ hoanTac: { nhan: "mốc thử" } }}
        view={view}
        canEdit={false}
        loading={false}
        guestResult={{}}
        residentResult={{}}
        mode="grid"
        onModeChange={vi.fn()}
        fullscreen={false}
        onFullscreenChange={vi.fn()}
        onSaveSchedule={vi.fn()}
        onHoanTac={vi.fn()}
        onXuatLuoi={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: "Xuất lưới" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Toàn màn hình" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Lưu thời khoá biểu" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Huỷ thay đổi" })).not.toBeInTheDocument();
  });
});
