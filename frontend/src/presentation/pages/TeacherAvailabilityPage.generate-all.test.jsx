import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TeacherAvailabilityPage from "./TeacherAvailabilityPage";

let appData;

vi.mock("../../context/AppDataContext", () => ({
  useAppData: () => appData,
}));

const teachers = [
  { id: 1, name: "GV thỉnh giảng", type: "GUEST", org: "Ngoài trường", availabilitySlots: [1] },
  { id: 2, name: "GV cơ hữu", type: "RESIDENT", org: "VJU", availabilitySlots: [] },
  { id: 3, name: "GV không có lớp", type: "RESIDENT", org: "VJU", availabilitySlots: [2] },
  { id: 4, name: "Phòng Đào tạo điều phối", type: "GUEST", isPlaceholder: true, availabilitySlots: [] },
];

beforeEach(() => {
  appData = {
    data: { teachers, classes: [] },
    loading: false,
    generateAllTeacherAvailability: vi.fn().mockResolvedValue({ generatedTeacherCount: 3 }),
  };
});

describe("TeacherAvailabilityPage - Khai toàn bộ giờ rảnh", () => {
  it("đặt nút ngay cạnh ô tìm kiếm và chỉ hiện cho người được sửa", () => {
    const { rerender } = render(<TeacherAvailabilityPage role="editor" />);
    const search = screen.getByRole("textbox", { name: /Tìm tên, email, đơn vị/i });
    const button = screen.getByRole("button", { name: /Khai toàn bộ giờ rảnh/i });
    expect(search.parentElement.parentElement.nextElementSibling).toBe(button);

    rerender(<TeacherAvailabilityPage role="viewer" />);
    expect(screen.queryByRole("button", { name: /Khai toàn bộ giờ rảnh/i })).not.toBeInTheDocument();
  });

  it("đếm toàn bộ giảng viên thật thuộc cả hai loại, không phụ thuộc tab hoặc tìm kiếm", async () => {
    const user = userEvent.setup();
    render(<TeacherAvailabilityPage role="editor" />);

    await user.type(screen.getByRole("textbox", { name: /Tìm tên, email, đơn vị/i }), "không khớp");
    await user.click(screen.getByRole("button", { name: /Khai toàn bộ giờ rảnh/i }));

    const dialog = screen.getByRole("dialog");
    expect(within(dialog).getByText(/3 giảng viên/i)).toBeInTheDocument();
    expect(within(dialog).getByText(/cả hai loại/i)).toBeInTheDocument();
    expect(within(dialog).getByText(/không phụ thuộc tab/i)).toBeInTheDocument();
    expect(within(dialog).getByText(/lịch đã chốt/i)).toBeInTheDocument();
  });

  it("Hủy không gọi API", async () => {
    const user = userEvent.setup();
    render(<TeacherAvailabilityPage role="editor" />);

    await user.click(screen.getByRole("button", { name: /Khai toàn bộ giờ rảnh/i }));
    await user.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Hủy" }));

    expect(appData.generateAllTeacherAvailability).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("chỉ gọi một API sau xác nhận, khóa thao tác khi đang chạy và đóng khi thành công", async () => {
    const user = userEvent.setup();
    let resolveRequest;
    appData.generateAllTeacherAvailability = vi.fn(() => new Promise((resolve) => {
      resolveRequest = resolve;
    }));
    render(<TeacherAvailabilityPage role="editor" />);

    await user.click(screen.getByRole("button", { name: /Khai toàn bộ giờ rảnh/i }));
    const confirm = within(screen.getByRole("dialog")).getByRole("button", { name: "Xác nhận" });
    await user.click(confirm);

    expect(appData.generateAllTeacherAvailability).toHaveBeenCalledTimes(1);
    expect(within(screen.getByRole("dialog")).getByRole("button", { name: /Đang xử lý/i })).toBeDisabled();
    expect(within(screen.getByRole("dialog")).getByRole("button", { name: "Hủy" })).toBeDisabled();

    resolveRequest({ generatedTeacherCount: 3 });
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(appData.generateAllTeacherAvailability).toHaveBeenCalledTimes(1);
  });

  it("giữ hộp thoại mở khi API lỗi và vô hiệu nút khi không có giảng viên thật", async () => {
    const user = userEvent.setup();
    appData.generateAllTeacherAvailability = vi.fn().mockRejectedValue(new Error("Lỗi mạng"));
    const { rerender } = render(<TeacherAvailabilityPage role="editor" />);

    await user.click(screen.getByRole("button", { name: /Khai toàn bộ giờ rảnh/i }));
    await user.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Xác nhận" }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    await user.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Hủy" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());

    appData = { ...appData, data: { teachers: [teachers[3]], classes: [] } };
    rerender(<TeacherAvailabilityPage role="editor" />);
    expect(screen.getByRole("button", { name: /Khai toàn bộ giờ rảnh/i })).toBeDisabled();
  });
});
