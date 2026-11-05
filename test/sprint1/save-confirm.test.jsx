import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ScheduleActions } from "@/presentation/schedule/ScheduleToolbar";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

function renderActions(onSaveSchedule) {
  render(
    <ScheduleActions
      data={{}}
      view={{ lessons: [{ id: 1 }] }}
      canEdit
      loading={false}
      guestResult={{ lessons: [{ id: 1 }] }}
      residentResult={{ lessons: [{ id: 2 }] }}
      mode="grid"
      onModeChange={vi.fn()}
      fullscreen={false}
      onFullscreenChange={vi.fn()}
      onSaveSchedule={onSaveSchedule}
      onHoanTac={vi.fn()}
      onXuatLuoi={vi.fn()}
    />,
  );
}

describe("Sprint 1 S1-23 — xác nhận lưu toàn bộ lịch", () => {
  it("S1-23/Hủy: không gọi lưu và thông báo nói rõ TOÀN BỘ lớp", async () => {
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(false);
    const save = vi.fn();
    renderActions(save);
    await userEvent.click(screen.getByRole("button", { name: "Lưu thời khoá biểu" }));
    expect(confirm).toHaveBeenCalledOnce();
    expect(confirm).toHaveBeenCalledWith(expect.stringContaining("TOÀN BỘ lớp"));
    expect(save).not.toHaveBeenCalled();
  });

  it("S1-23/Đồng ý: lưu đúng một lần và không truyền bộ lọc đang xem", async () => {
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(true);
    const save = vi.fn();
    renderActions(save);
    await userEvent.click(screen.getByRole("button", { name: "Lưu thời khoá biểu" }));
    expect(confirm).toHaveBeenCalledWith(expect.stringContaining("TOÀN BỘ lớp"));
    expect(save).toHaveBeenCalledOnce();
    expect(save.mock.calls[0]).toEqual([]);
  });
});
