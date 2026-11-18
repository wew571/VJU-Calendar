# Luồng hoạt động xếp thời khóa biểu

```text
Dữ liệu học phần có sẵn
        ↓
Quản lý giảng viên thỉnh giảng và cập nhật giờ có thể dạy
        ↓
Khai báo giờ rảnh của giảng viên cơ hữu
        ↓
Xếp lịch: GĐCT theo CTĐT phụ trách hoặc Trợ lý khoa trên phạm vi toàn trường
        ↓
Kiểm tra kết quả, xử lý vấn đề, lưu hoặc xuất lịch
```

## 1. Chuẩn bị dữ liệu học phần

Dữ liệu lớp học phần cần có trong hệ thống trước khi xếp lịch. Hiện chưa phân công vai trò nào được nhập/sửa dữ liệu học phần hoặc nạp Excel, nên bước này được xem là đầu vào có sẵn, chưa thuộc luồng thao tác của các hồ sơ vai trò hiện tại.

## 2. Chuẩn bị giảng viên thỉnh giảng

**GĐCT, ĐPCT hoặc Trợ lý khoa** có thể mời giảng viên thỉnh giảng, nhập/cập nhật hồ sơ và khai báo giờ có thể dạy. Thông tin này được dùng để chuẩn bị lịch cho các lớp có giảng viên thỉnh giảng.

## 3. Khai báo giờ rảnh cơ hữu

Giảng viên cơ hữu tự khai giờ rảnh. **Trợ lý khoa** có thể nhập hoặc cập nhật giờ rảnh thay giảng viên. Trong bản demo, hồ sơ cơ hữu được chọn để thao tác chỉ là hồ sơ mô phỏng, không xác minh danh tính.

## 4. Xếp lịch

- **GĐCT** chọn CTĐT được giao và xếp lịch trong phạm vi CTĐT đó.
- **Trợ lý khoa** có thể xếp lịch thay GĐCT khi cần, trên phạm vi toàn trường.
- **ĐPCT không được cấp quyền xếp lịch.**

Hệ thống giữ nguyên luồng giải hiện có: xếp giảng viên thỉnh giảng trước, sau đó ghép giảng viên cơ hữu vào các giờ còn phù hợp.

## 5. Rà soát và hoàn tất

Người có quyền xếp lịch kiểm tra kết quả và các vấn đề được hệ thống báo; có thể chỉnh lịch thủ công theo chức năng hiện có, sau đó lưu hoặc xuất kết quả.

## Giới hạn của luồng hiện tại

- Vai trò trên giao diện chỉ mô phỏng luồng thao tác, không phải đăng nhập hay cơ chế bảo vệ API.
- Hồ sơ giảng viên thỉnh giảng hiện chưa gắn với CTĐT nên danh sách hồ sơ được dùng chung.
- Mục 6 tạm hoãn; chưa bổ sung vai trò đăng nhập riêng cho JLE hoặc Phòng Đào tạo.
