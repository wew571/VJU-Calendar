# Báo cáo thay đổi VJU-Calendar

## Mục tiêu

Cập nhật giao diện và tài liệu theo yêu cầu phân vai nghiệp vụ mới, đồng thời giữ nguyên thuật toán và các ràng buộc xếp lịch hiện có.

## Thay đổi chính

### Vai trò và phạm vi thao tác

- Tách các hồ sơ giao diện thành Giám đốc CT (GĐCT), Điều phối CT (ĐPCT), Trợ lý khoa, Giảng viên cơ hữu và Xem thôi.
- GĐCT xếp lịch trong CTĐT được chọn; Trợ lý khoa có thể xếp lịch trên phạm vi toàn trường; ĐPCT không được cấp quyền xếp lịch.
- GĐCT, ĐPCT và Trợ lý khoa có thể mời giảng viên thỉnh giảng, cập nhật hồ sơ và giờ có thể dạy.
- Giảng viên cơ hữu có thể khai giờ rảnh cho hồ sơ được chọn trong bản demo; Trợ lý khoa có thể cập nhật giờ rảnh cơ hữu.
- Chưa phân quyền nhập/sửa dữ liệu học phần hoặc nạp Excel vì yêu cầu chưa xác định vai trò phụ trách. Mục tương ứng không được đưa vào menu các hồ sơ vai trò.

### Giao diện

- Cập nhật màn hình chọn hồ sơ, điều hướng, nhãn vai trò và nội dung hướng dẫn theo các quyền mới.
- Giới hạn phạm vi xem và xếp lịch của GĐCT theo CTĐT đã chọn.
- Làm rõ bộ đếm trong Chuẩn bị dữ liệu: số nhóm điều phối viên còn việc được phân biệt với tổng số nhóm có trong dữ liệu; đây không phải số CTĐT. Các số liệu lấy động từ dữ liệu.
- Sửa trang Giảng viên để hồ sơ Giảng viên cơ hữu mở trực tiếp ở tab Cơ hữu. Hướng dẫn chọn hồ sơ đại diện và thông báo rõ khi dữ liệu chưa có hồ sơ cơ hữu.

### Tài liệu

Cập nhật mô tả nghiệp vụ trong README, tài liệu quy trình, đặc tả hệ thống, phân tích ràng buộc, README frontend, hướng dẫn trong ứng dụng và ghi chú góp ý liên quan đến bộ đếm.

## Giới hạn và điểm chưa xác định

- Vai trò chọn trên giao diện chỉ mô phỏng luồng thao tác; ứng dụng chưa có đăng nhập hoặc phân quyền tài khoản/API thật.
- Hồ sơ giảng viên thỉnh giảng chưa gắn với CTĐT, vì vậy chưa giới hạn được danh sách hồ sơ theo phạm vi CTĐT của GĐCT/ĐPCT.
- Hồ sơ giảng viên cơ hữu được chọn trong bản demo không xác minh danh tính người thao tác.
- Chưa xác định vai trò được phép nhập/sửa dữ liệu học phần và nạp Excel.
- Mục 6 được tạm hoãn. Không bổ sung vai trò đăng nhập riêng cho JLE hoặc Phòng Đào tạo.
- Chưa cập nhật hướng dẫn DOCX do môi trường thực hiện không có công cụ chỉnh sửa DOCX phù hợp.

## Kiểm tra

- Build frontend: thành công.
- Test phân quyền mục tiêu: 3/3 đạt.
- Test luồng chọn hồ sơ cơ hữu: 2/2 đạt.
- `git diff --check`: đạt.
- Toàn bộ test hiện có: lần chạy gần nhất ghi nhận 120 test đạt và 19 test lỗi trên 25 file. Các lỗi còn lại gồm mock test thiếu export và các kỳ vọng cũ về hướng dẫn, điều hướng, tìm kiếm hoặc giao diện; chưa xử lý trong phạm vi báo cáo này.

## Các tệp liên quan

- `frontend/src/constants/roles.js`
- `frontend/src/constants/nav.js`
- `frontend/src/App.jsx`
- `frontend/src/presentation/RolePickerScreen.jsx`
- `frontend/src/presentation/pages/SchedulePage.jsx`
- `frontend/src/presentation/pages/TeacherAvailabilityPage.jsx`
- `frontend/src/presentation/pages/SubmissionsPage.jsx`
- `frontend/src/presentation/pages/GuidePage.jsx`
- `frontend/src/presentation/manual/TeacherEditDrawer.jsx`
- `README.md`, `frontend/README.md`
- `doc/QUY-TRINH-NGHIEP-VU-XEP-TKB.md`
- `doc/PHAN-TICH-RANG-BUOC.md`
- `doc/System specification.md`
- `VJU-Calendar-gop-y.md`
- `test/frontend/roles.test.js`
- `test/frontend/resident-availability.test.jsx`
