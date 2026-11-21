import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TeacherAvailabilityPage from "@/presentation/pages/TeacherAvailabilityPage";

const appData = vi.hoisted(() => ({ current: null }));

vi.mock("@/context/AppDataContext", () => ({
  useAppData: () => appData.current,
}));

beforeEach(() => {
  localStorage.clear();
  appData.current = {
    data: {
      numDays: 6,
      slotsPerDay: 12,
      classes: [],
      teachers: [
        { id: 1, name: "Guest Lecturer", nameRaw: "Guest Lecturer", type: "GUEST", org: "Other University", availabilitySlots: [1] },
        { id: 2, name: "Resident Lecturer", nameRaw: "Resident Lecturer", type: "RESIDENT", org: "VJU", availabilitySlots: [] },
      ],
    },
    loading: false,
    updateManualTeacher: vi.fn().mockResolvedValue({ ok: true }),
    generateAllTeacherAvailability: vi.fn(),
  };
});

describe("Sprint 2 supplemental resident availability behavior", () => {
  it("S2-BS-16: records that resident role does not currently select the resident tab", () => {
    render(<TeacherAvailabilityPage role="resident" />);

    expect(screen.getByRole("tab", { name: /thỉnh giảng/i })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: /cơ hữu/i })).toHaveAttribute("aria-selected", "false");
    expect(screen.queryByRole("combobox", { name: /chọn hồ sơ giảng viên cơ hữu/i })).not.toBeInTheDocument();
  });

  it("S2-BS-17: shows the empty-list state after manually opening the resident tab", async () => {
    const user = userEvent.setup();
    appData.current.data.teachers = [appData.current.data.teachers[0]];
    render(<TeacherAvailabilityPage role="resident" />);

    await user.click(screen.getByRole("tab", { name: /cơ hữu/i }));
    expect(screen.getByText("Không có giảng viên cơ hữu nào khớp.")).toBeInTheDocument();
    expect(screen.queryByText(/chưa có hồ sơ giảng viên cơ hữu trong dữ liệu/i)).not.toBeInTheDocument();
  });

  it("S2-BS-19: saves selected availability for the resident row to the mocked context boundary", async () => {
    const user = userEvent.setup();
    const updateManualTeacher = appData.current.updateManualTeacher;
    render(<TeacherAvailabilityPage role="resident" />);

    await user.click(screen.getByRole("tab", { name: /cơ hữu/i }));
    await user.click(screen.getByRole("row", { name: /Resident Lecturer/ }));
    expect(screen.getByRole("dialog", { name: "Sửa giảng viên #2" })).toBeInTheDocument();

    const slot = screen.getByRole("checkbox", { name: "Thứ 2 tiết 1" });
    slot.focus();
    await user.keyboard(" ");
    expect(slot).toHaveAttribute("aria-checked", "true");
    await user.click(screen.getByRole("button", { name: "Lưu 1 khung giờ" }));

    await waitFor(() => expect(updateManualTeacher).toHaveBeenCalledWith(2, { availability: [0] }));
    expect(updateManualTeacher).toHaveBeenCalledTimes(1);
  });
});
