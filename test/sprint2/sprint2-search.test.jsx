import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ManualEntryPage from "@/presentation/pages/ManualEntryPage";

const qa = vi.hoisted(() => ({ classes: [] }));
vi.mock("@/context/AppDataContext", () => ({
  useAppData: () => ({
    data: { sourceLabel: "QA Sprint 2", classes: qa.classes, teachers: [], courses: [] },
    loading: false,
  }),
}));
// Keep the real search/filter page. Replace only table rendering and unrelated forms.
vi.mock("@/presentation/manual/SectionTable", () => ({
  STATUS_META: { ready_auto: { label: "Tự động xếp", tone: "amber" } },
  default: ({ rows, onOpenSection }) => (
    <div data-testid="matching-sections">
      {rows.map((row) => <button key={row.sectionId} onClick={onOpenSection(row.sectionId)}>{row.sectionId}</button>)}
    </div>
  ),
}));
vi.mock("@/presentation/manual/SectionEditDrawer", () => ({
  default: ({ section }) => <div data-testid="opened-section">{section?.sectionId}</div>,
}));
vi.mock("@/presentation/manual/TeacherEditDrawer", () => ({ default: () => null }));
vi.mock("@/presentation/manual/CourseEditDrawer", () => ({ default: () => null }));
vi.mock("@/presentation/manual/ImportExcelDialog", () => ({ default: () => null }));
vi.mock("@/presentation/manual/ExportExcelDialog", () => ({ default: () => null }));
vi.mock("@/presentation/manual/ChotCourseDialog", () => ({ default: () => null }));

beforeEach(() => {
  vi.stubGlobal("ResizeObserver", class { observe() {} disconnect() {} });
  qa.classes = [
    { sectionId: 0, classCode: "QA-ZERO", courseName: "Môn không", teacherName: "GV QA B", programParts: ["BCE"], cohortParts: ["K2026"] },
    { sectionId: 19, classCode: "QA-CSE19", courseName: "Kiểm thử phần mềm", teacherName: "GV QA A", programParts: ["CSE"], cohortParts: ["K2025"] },
    { sectionId: 190, classCode: "QA-CSE190", courseName: "Môn khác", teacherName: "GV QA C", programParts: ["BCE"], cohortParts: ["K2026"] },
  ].map((row) => ({ status: "ready_auto", sectionChot: null, ...row }));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

function search(value) {
  fireEvent.change(screen.getByRole("textbox", { name: /Tìm mã lớp/ }), { target: { value } });
}
function ids() {
  return within(screen.getByTestId("matching-sections")).queryAllByRole("button").map((button) => Number(button.textContent));
}

describe("Sprint 2 BL01 — exact class ID search", () => {
  it("S2-B01-01: #19 returns ID 19 without matching ID 190", () => {
    render(<ManualEntryPage role="staff" />);
    search("#19");
    expect(ids()).toEqual([19]);
  });

  it("S2-B01-02: #0 returns and opens class ID 0", async () => {
    render(<ManualEntryPage role="staff" />);
    search("#0");
    expect(ids()).toEqual([0]);
    await userEvent.click(within(screen.getByTestId("matching-sections")).getByRole("button", { name: "0" }));
    expect(screen.getByTestId("opened-section")).toHaveTextContent(/^0$/);
  });

  it("S2-B01-03: an absent ID yields zero results", () => {
    render(<ManualEntryPage role="staff" />);
    search("#999999");
    expect(ids()).toEqual([]);
  });

  it("S2-B01-04: malformed queries stay usable and do not resolve as one valid #id", () => {
    render(<ManualEntryPage role="staff" />);
    for (const query of ["#", "#abc", "#-1", "#19 #190"]) {
      search(query);
      expect(screen.getByRole("textbox", { name: /Tìm mã lớp/ })).toHaveValue(query);
      expect(ids()).not.toEqual([19]);
      expect(ids()).not.toEqual([190]);
      search("");
      expect(ids()).toEqual([0, 19, 190]);
    }
  });

  it("S2-B01-05: class, course, lecturer and plain-number search preserve the baseline", async () => {
    render(<ManualEntryPage role="staff" />);
    for (const [query, expected] of [
      ["QA-CSE19", [19, 190]], ["Kiểm thử phần mềm", [19]], ["GV QA A", [19]], ["19", [19, 190]],
    ]) {
      search(query);
      expect(ids()).toEqual(expected);
    }
    search("QA-ZERO");
    await userEvent.click(within(screen.getByTestId("matching-sections")).getByRole("button", { name: "0" }));
    expect(screen.getByTestId("opened-section")).toHaveTextContent(/^0$/);
  });

  it("S2-B01-06: #id obeys both programme and cohort filters", async () => {
    const user = userEvent.setup();
    render(<ManualEntryPage role="staff" />);
    search("#19");
    await user.click(screen.getByRole("button", { name: "Mọi chương trình" }));
    await user.click(screen.getByRole("menuitem", { name: "CSE" }));
    expect(ids()).toEqual([19]);
    await user.click(screen.getByRole("button", { name: "CSE" }));
    await user.click(screen.getByRole("menuitem", { name: "BCE" }));
    expect(ids()).toEqual([]);
    await user.click(screen.getByRole("button", { name: "BCE" }));
    await user.click(screen.getByRole("menuitem", { name: "Tất cả" }));
    await user.click(screen.getByRole("button", { name: "Mọi khoá" }));
    await user.click(screen.getByRole("menuitem", { name: "K2025" }));
    expect(ids()).toEqual([19]);
    await user.click(screen.getByRole("button", { name: "K2025" }));
    await user.click(screen.getByRole("menuitem", { name: "K2026" }));
    expect(ids()).toEqual([]);
  });
});
