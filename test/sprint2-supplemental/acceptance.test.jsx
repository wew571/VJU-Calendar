import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RolePickerScreen from "@/presentation/RolePickerScreen";
import SubmissionsPage from "@/presentation/pages/SubmissionsPage";
import { getAllowedGroups } from "@/constants/nav";

const context = vi.hoisted(() => ({ current: null }));
vi.mock("@/context/AppDataContext", () => ({
  useAppData: () => context.current,
}));

function submission(sectionId, coordinator, teacherId, windowSlots = []) {
  return {
    sectionId,
    coordinator,
    coordinators: [coordinator],
    teacherId,
    teacherType: "GUEST",
    teacherName: `Guest ${teacherId}`,
    courseName: `Course ${sectionId}`,
    programLabel: "BCSE",
    programParts: ["BCSE"],
    roomType: "LT",
    duration: 2,
    windowSlots,
    availabilityAssumed: false,
  };
}

function fixture() {
  return {
    numDays: 7,
    slotsPerDay: 13,
    classes: [],
    teachers: [
      { id: 1, name: "Guest 1", type: "GUEST" },
      { id: 2, name: "Guest 2", type: "GUEST" },
      { id: 3, name: "Resident 3", type: "RESIDENT" },
    ],
    submissions: [
      submission(11, "Coordinator A", 1),
      submission(12, "Coordinator A", 1),
      submission(21, "Coordinator B", 2),
      submission(31, "Coordinator C", 2, [26]),
      { ...submission(41, "Resident coordinator", 3), teacherType: "RESIDENT" },
      { ...submission(51, "Excluded coordinator", 2), boQua: true },
    ],
  };
}

beforeEach(() => {
  context.current = {
    data: fixture(),
    loading: false,
    error: null,
    updateManualTeacher: vi.fn().mockResolvedValue({ ok: true }),
  };
});
afterEach(cleanup);

describe("Sprint 2 supplemental acceptance against current production components", () => {
  it("S2-BS-01: role picker exposes the two roles implemented by the current demo", () => {
    render(<RolePickerScreen onPick={vi.fn()} />);
    expect(screen.getByRole("button", { name: /Giáo vụ \/ Điều phối viên/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Xem thôi/i })).toBeInTheDocument();
    expect(screen.getByText(/không dùng để vận hành chính thức/i)).toBeInTheDocument();
  });

  it("S2-BS-02: selecting staff sends the implemented role to the callback", async () => {
    const user = userEvent.setup();
    const onPick = vi.fn();
    render(<RolePickerScreen onPick={onPick} />);
    await user.click(screen.getByRole("button", { name: /Giáo vụ \/ Điều phối viên/i }));
    expect(onPick).toHaveBeenCalledWith("staff");
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
  });

  it("observes current navigation for staff and viewer; this does not prove the requested five-profile matrix", () => {
    expect(getAllowedGroups("staff").map(({ key }) => key)).toEqual(["manual", "data", "history"]);
    expect(getAllowedGroups("viewer").map(({ key }) => key)).toEqual(["history"]);
  });

  it("S2-BS-20: submissions exposes its current queue, lookup, and coordinator views", () => {
    render(<SubmissionsPage role="staff" />);
    expect(screen.getByRole("tab", { name: /Cần xử lý.*3/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Bảng tra cứu.*4/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Theo điều phối viên.*2/i })).toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: /Nhóm điều phối viên còn việc/i })).not.toBeInTheDocument();
  });

  it("observes the current work-queue count changing when fixture data is refreshed", async () => {
    const { rerender } = render(<SubmissionsPage role="staff" />);
    expect(screen.getByRole("tab", { name: /Cần xử lý.*3/ })).toBeVisible();

    context.current = {
      ...context.current,
      data: {
        ...context.current.data,
        submissions: context.current.data.submissions.map((row) =>
          row.coordinator === "Coordinator A"
            ? { ...row, windowSlots: Array.from({ length: 76 }, (_, slot) => slot) }
            : row,
        ),
      },
    };
    rerender(<SubmissionsPage role="staff" />);
    expect(screen.getByRole("tab", { name: /Cần xử lý.*1/ })).toBeVisible();
  });
});
