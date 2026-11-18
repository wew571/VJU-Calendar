import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import GuidePage from "@/presentation/pages/GuidePage";

afterEach(cleanup);

function allGuideText() {
  const view = render(<GuidePage />);
  const sections = ["Tổng quan", "Luồng làm việc", "Màn hình chính", "Nhập từ Excel", "Thuật ngữ", "Checklist kiểm thử", "Giới hạn & FAQ"];
  return sections.map((name) => {
    fireEvent.click(screen.getByRole("button", { name, exact: true }));
    return view.container.textContent.replace(/\s+/g, " ");
  }).join("\n");
}

// Content checks cover only the in-app documentation portion of BL03.
// Repo review and observation of save/undo/export behavior remain manual.
describe("Sprint 2 BL03 — persistence guidance content", () => {
  it("S2-B03-01: guidance describes JSON persistence and removes the shutdown-loss claim [app content only]", () => {
    const text = allGuideText();
    expect(text).toMatch(/JSON/i);
    expect(text).not.toMatch(/mất (?:hết )?(?:dữ liệu|khi tắt)|tắt[^.\n]{0,70}mất hết dữ liệu/i);
  });

  it("S2-B03-02: guidance distinguishes unsaved drafts, saved timetable and undo checkpoint [app content only]", () => {
    const text = allGuideText();
    expect(text).toMatch(/nháp|chưa lưu|chưa áp dụng/i);
    expect(text).toMatch(/Lưu thời kho[aá] biểu/i);
    expect(text).toMatch(/mốc[^.\n]{0,100}(?:hoàn tác|Hủy thay đổi)|Hủy thay đổi[^.\n]{0,100}mốc/i);
  });

  it("S2-B03-03: Excel export is explicitly distinguished from a full backup and server restore [app content only]", () => {
    const text = allGuideText();
    expect(text).toMatch(/(?:xuất|Excel)[^.\n]{0,180}không[^.\n]{0,120}(?:backup|sao lưu)|không[^.\n]{0,100}(?:backup|sao lưu)[^.\n]{0,100}(?:Excel|xuất)/i);
    expect(text).toMatch(/(?:khôi phục|phục hồi)[^.\n]{0,100}(?:server|máy chủ)|(?:server|máy chủ)[^.\n]{0,100}(?:khôi phục|phục hồi)/i);
  });
});
