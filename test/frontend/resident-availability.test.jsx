import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TeacherAvailabilityPage from "@/presentation/pages/TeacherAvailabilityPage";

let appData;

vi.mock("@/context/AppDataContext", () => ({
  useAppData: () => appData,
}));

beforeEach(() => {
  localStorage.clear();
  appData = {
    data: {
      classes: [],
      teachers: [
        { id: 1, name: "Giảng viên thỉnh giảng", nameRaw: "Giảng viên thỉnh giảng", type: "GUEST" },
        { id: 2, name: "Giảng viên cơ hữu", nameRaw: "Giảng viên cơ hữu", type: "RESIDENT" },
      ],
    },
    loading: false,
  };
});

describe("resident availability profile", () => {
  it("opens on the resident list and shows the selected profile data", async () => {
    const user = userEvent.setup();
    render(<TeacherAvailabilityPage role="resident" />);

    expect(screen.getByRole("tab", { name: /cơ hữu/ })).toHaveAttribute("aria-selected", "true");
    expect(screen.queryByRole("tab", { name: /thỉnh giảng/ })).not.toBeInTheDocument();
    expect(screen.getByText("Hãy chọn hồ sơ giảng viên cơ hữu để xem dữ liệu.")).toBeInTheDocument();

    await user.selectOptions(
      screen.getByRole("combobox", { name: "Chọn hồ sơ giảng viên cơ hữu trong bản demo" }),
      "2",
    );

    expect(screen.getByRole("cell", { name: "Giảng viên cơ hữu" })).toBeInTheDocument();
  });

  it("explains when no resident profile exists in the loaded data", () => {
    appData = {
      ...appData,
      data: { ...appData.data, teachers: [appData.data.teachers[0]] },
    };

    render(<TeacherAvailabilityPage role="resident" />);

    expect(screen.getByText("Chưa có hồ sơ giảng viên cơ hữu trong dữ liệu.")).toBeInTheDocument();
    expect(screen.getByText(/Chưa có hồ sơ giảng viên cơ hữu trong dữ liệu hiện tại\./))
      .toBeInTheDocument();
  });
});
