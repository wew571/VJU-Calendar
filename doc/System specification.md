# ĐẶC TẢ HỆ THỐNG VJU-CALENDAR

**Hệ thống hỗ trợ xếp thời khóa biểu tự động — Trường Đại học Việt Nhật (VJU)**

| Thuộc tính | Giá trị |
|---|---|
| Tên hệ thống | VJU-Calendar |
| Phiên bản tài liệu | 2.0 |
| Ngày cập nhật | 23/09/2026 |
| Bản chất tài liệu | Đặc tả yêu cầu và thiết kế, viết **trước khi triển khai mã nguồn** |

> Tài liệu này được soạn theo trình tự phát triển chuẩn: phân tích nghiệp vụ → đặc tả yêu cầu → thiết kế hệ thống → lập kế hoạch triển khai. Người mới tiếp nhận dự án đọc tài liệu này để hiểu hệ thống cần xây dựng là gì, vì sao thiết kế như vậy và sẽ nghiệm thu theo tiêu chí nào.

## 1. Giới thiệu

### 1.1. Mục đích tài liệu

Đặc tả toàn diện yêu cầu chức năng, yêu cầu phi chức năng, ràng buộc nghiệp vụ và phương án thiết kế của hệ thống VJU-Calendar, làm cơ sở để triển khai mã nguồn và nghiệm thu sản phẩm. Tài liệu được viết trước khi bắt đầu lập trình; mọi quyết định kỹ thuật trong tài liệu đều kèm lý do.

### 1.2. Phạm vi hệ thống

VJU-Calendar là công cụ phần mềm hỗ trợ Phòng Đào tạo và giáo vụ khoa xây dựng thời khóa biểu (TKB) học kỳ, với các năng lực cần có:

- Tự động xếp lịch bằng bộ giải ràng buộc, theo chiến lược hai giai đoạn: xếp lớp giảng viên thỉnh giảng trước, ghép lớp giảng viên cơ hữu sau.
- Hỗ trợ điều chỉnh bán tự động: kéo-thả, ghim, chốt lịch; cảnh báo xung đột tức thời.
- Trao đổi dữ liệu với file Excel kế hoạch giảng dạy (nhập có kiểm tra, xuất hoàn chỉnh).

Ngoài phạm vi: phân quyền theo tài khoản, gán phòng học cụ thể theo tên, quản lý đăng ký môn của sinh viên, xếp lịch thi, tích hợp hệ thống quản lý đào tạo khác.

### 1.3. Đối tượng đọc tài liệu

| Đối tượng | Điều cần biết |
|---|---|
| Giáo vụ, điều phối viên | Hệ thống sẽ hỗ trợ công việc của họ ra sao, quy trình vận hành thế nào. |
| Nhà phát triển | Sẽ xây dựng những gì, thiết kế ra sao, nghiệm thu theo tiêu chí nào. |
| Người nghiệm thu | Cơ sở đối chiếu giữa yêu cầu và sản phẩm bàn giao. |

### 1.4. Thuật ngữ và định nghĩa

| Thuật ngữ | Định nghĩa |
|---|---|
| Lớp học phần | Một lớp khai giảng của một học phần; đơn vị cơ bản được xếp lịch. |
| Giảng viên thỉnh giảng (GUEST) | Giảng viên mời ngoài, chỉ dạy trong các khung giờ đã khai báo. |
| Giảng viên cơ hữu (RESIDENT) | Giảng viên biên chế, có thể xếp vào mọi ô giờ còn trống hợp lệ. |
| Nhóm sinh viên | Cặp (chương trình đào tạo × khóa); không thể học hai môn cùng lúc. |
| Khối ca | Khoảng tiết liên tục trong ngày; một buổi học phải nằm gọn trong một khối. |
| Học chung | Nhiều mã lớp ghi lại cùng một buổi dạy vật lý, chiếm đúng một suất phòng. |
| Chốt học phần | Khóa giờ của mọi lớp thuộc một học phần, mọi thao tác đổi giờ bị từ chối. |
| Ghim (pin) | Buổi đã sửa tay và lưu; giữ nguyên vị trí qua các lần giải lại. |
| Phạm vi xếp | Giải riêng một chương trình/khóa nhưng vẫn né lịch của phần còn lại. |
| FATE | Khuôn chuẩn file Excel kế hoạch giảng dạy dùng làm đầu vào/đầu ra. |
| CP-SAT | Bộ giải ràng buộc tổ hợp (Google OR-Tools) dự kiến sử dụng. |
| Pool phòng | Tổng số suất phòng lý thuyết/thực hành dùng đồng thời, chưa gán tên phòng. |

### 1.5. Tài liệu nghiệp vụ đầu vào

Hai tài liệu phân tích nghiệp vụ được hoàn thành trước tài liệu này và là căn cứ trực tiếp của đặc tả:

| Tài liệu | Nội dung |
|---|---|
| Phân tích ràng buộc xếp TKB | Toàn bộ quy tắc nghiệp vụ: ràng buộc cứng, ràng buộc mềm, thứ tự ưu tiên. |
| Quy trình nghiệp vụ xếp TKB — 3 vai trò | Luồng công việc GĐCT → Giáo vụ khoa → Phòng Đào tạo. |

## 2. Miêu tả tổng thể

### 2.1. Bối cảnh và vấn đề

Mỗi học kỳ, trường phải xếp lịch cho hàng trăm lớp học phần, đồng thời cân đối: giờ rảnh của giảng viên thỉnh giảng, lịch của các nhóm sinh viên, số lượng phòng theo loại tại hai cơ sở (Hòa Lạc, Mỹ Đình) và các thỏa thuận giờ đã chốt với giảng viên ngoài trường. Cách làm thủ công dễ phát sinh trùng lịch, khó kiểm tra chéo giữa các chương trình và tiêu tốn nhiều thời gian công.

### 2.2. Mục tiêu và tiêu chí thành công

**Mục tiêu:** (1) tự động hóa tính toán xếp lịch; (2) giữ quyền quyết định cuối cùng cho con người thông qua chế độ bán tự động; (3) giảm sai sót và thời gian làm việc nhờ trao đổi trực tiếp với file Excel kế hoạch giảng dạy.

**Tiêu chí thành công** (đo được khi nghiệm thu):

1. Một lần giải hoàn tất trong thời gian giới hạn cấu hình được (dự kiến 30 giây).
2. Kết quả giải không chứa xung đột cứng: không trùng giảng viên, không vượt pool phòng, buổi học luôn nằm gọn trong khối ca.
3. Mọi thao tác phá hủy dữ liệu đều có bước xác nhận; tồn tại cơ chế hoàn tác.
4. Vòng lặp Excel khép kín: file xuất ra có thể nạp lại làm đầu vào cho kỳ sau.
5. Cảnh báo xung đột hiển thị ngay khi người dùng sửa tay.

### 2.3. Bên liên quan

| Bên liên quan | Mối quan tâm |
|---|---|
| Giáo vụ / điều phối viên khoa | Người dùng trực tiếp; muốn xếp nhanh, ít sai, kiểm soát được mọi thay đổi. |
| Giám đốc chương trình đào tạo | Muốn lớp của chương trình mình được xếp đúng khung giờ đã chốt với giảng viên. |
| Phòng Đào tạo | Quản lý phòng toàn trường; cần nhận được TKB đã có giờ của các khoa. |
| Giảng viên | Không bị xếp trùng giờ, không dạy hai cơ sở trong một ngày, lịch gọn gàng. |
| Sinh viên | Người hưởng lợi cuối; không bị hai môn chùng giờ trong cùng nhóm. |
| Nhà phát triển | Cấu trúc rõ ràng, tách nghiệp vụ khỏi giao tiếp, dễ kiểm thử. |

### 2.4. Giả định và ràng buộc của dự án

- Công cụ nội bộ chạy trên máy của giáo vụ, không cần tài khoản đăng nhập, không kết nối ra Internet.
- Dữ liệu đầu vào chính là file Excel kế hoạch giảng dạy của trường; hệ thống không thể yêu cầu thay đổi cách nhập liệu hiện hành.
- Dữ liệu thực tế đã chứa một số xung đột do con người chốt sẵn; hệ thống phải chấp nhận tồn tại chúng thay vì cấm tuyệt đối.
- Kết quả xếp lịch mang tính tham khảo; quyết định cuối cùng thuộc giáo vụ.

### 2.5. Luồng nghiệp vụ tổng thể

Trình tự sử dụng chính mà hệ thống phải phục vụ:

1. **Nạp dữ liệu** — giáo vụ nhập file Excel kế hoạch giảng dạy (hoặc nhập tay) vào hệ thống.
2. **Chuẩn bị giờ** — điều phối viên nộp khung giờ cho các lớp thỉnh giảng chưa có giờ; khai báo giờ rảnh giảng viên.
3. **Giải Giai đoạn 1** — hệ thống xếp các lớp thỉnh giảng vào khung giờ đã báo.
4. **Giải Giai đoạn 2** — hệ thống ghép các lớp cơ hữu vào chỗ còn trống.
5. **Tinh chỉnh** — giáo vụ xem hộp thư vấn đề, kéo-thả sửa tay, ghim, chốt; lưu và xuất file Excel hoàn chỉnh.

## 3. Yêu cầu chức năng

Yêu cầu chức năng được mã hóa `FR-x`, nhóm theo bốn cụm; diễn đạt dưới dạng "hệ thống phải".

### 3.1. Quản lý dữ liệu học phần

Bảng dữ liệu học phần là nguồn dữ liệu duy nhất của toàn hệ thống, phản chiếu cấu trúc file Excel kế hoạch giảng dạy gốc.

| Mã | Yêu cầu | Mô tả |
|---|---|---|
| FR-A1 | Quản lý giảng viên | Thêm/sửa/xoá giảng viên: họ tên, đơn vị, học hàm/vị, email, SĐT, loại (thỉnh giảng/cơ hữu); giảng viên thỉnh giảng kèm khai báo giờ có thể dạy theo từng tiết. |
| FR-A2 | Quản lý học phần | Thêm/sửa học phần: mã, tên, số tín chỉ. |
| FR-A3 | Quản lý lớp học phần | Tạo lớp từ giảng viên + học phần; khai Thứ/Tiết cố định hoặc đánh dấu "để hệ thống tự xếp". |
| FR-A4 | Nhập Excel hai bước | Bước chuẩn hoá: đọc file, hiển thị bảng xem trước, **chưa ghi** dữ liệu; phát hiện và yêu cầu xử lý dữ liệu bất thường (hai nguồn giờ trong file cũ ghi lệch nhau, dòng trùng, lớp chưa có giảng viên...). Bước nạp: ghi chính thức sau khi người dùng xác nhận; nạp mới thay thế toàn bộ dữ liệu cũ. |
| FR-A5 | Xuất Excel chuẩn | Xuất toàn bộ dữ liệu học phần ra file Excel khuôn chuẩn FATE, dùng làm văn bản chính thức và nạp lại cho kỳ sau. |
| FR-A6 | Xoá giờ hàng loạt | Đặt lại Thứ/Tiết của các lớp đang hiển thị theo bộ lọc hiện tại về "tự xếp". |
| FR-A7 | Bắt đầu học kỳ mới | Xoá toàn bộ dữ liệu về trạng thái trống để nhập liệu cho kỳ mới. |
| FR-A8 | Bỏ qua lớp đơn vị khác | Loại lớp do đơn vị khác điều phối khỏi bài toán xếp lịch; lớp đã có giờ vẫn hiển thị trên lưới và vẫn chiếm chỗ của nhóm sinh viên. |
| FR-A9 | Gom nhóm học chung | Gộp nhiều dòng của cùng một buổi dạy vật lý: cùng giờ, cùng được xếp hoặc cùng không, chiếm một suất phòng; mọi giảng viên trong nhóm bị coi là bận. |

### 3.2. Chuẩn bị dữ liệu giờ

| Mã | Yêu cầu | Mô tả |
|---|---|---|
| FR-B1 | Nộp khung giờ | Điều phối viên nộp một hoặc nhiều khung giờ khả dụng cho từng lớp thỉnh giảng chưa có giờ cố định. |
| FR-B2 | Khai báo giờ rảnh giảng viên | Tra cứu/khai báo giờ rảnh trong tuần theo từng tiết, đồng bộ với hồ sơ giảng viên. |
| FR-B3 | Tự động khai giờ rảnh | Sinh đề xuất giờ rảnh theo ba khung sáng/chiều/tối với xác suất theo số khung bận; luôn xác nhận trước khi thay toàn bộ giờ rảnh cũ; giữ nguyên giờ đang dạy; tuân thủ giới hạn ngày dạy theo loại giảng viên. |
| FR-B4 | Chặn giải khi chưa sẵn sàng | Từ chối chạy giải khi còn lớp thỉnh giảng thiếu giảng viên hoặc chưa có khung giờ; chỉ dẫn người dùng về màn chuẩn bị dữ liệu. |

### 3.3. Xếp và điều chỉnh thời khóa biểu

| Mã | Yêu cầu | Mô tả |
|---|---|---|
| FR-C1 | Giải Giai đoạn 1 | Xếp các lớp thỉnh giảng vào đúng một khung giờ đã báo; kết quả được lưu làm đầu vào bất biến cho Giai đoạn 2. |
| FR-C2 | Giải Giai đoạn 2 | Ghép lớp cơ hữu vào chỗ trống, né kết quả Giai đoạn 1 về giảng viên, pool phòng và nhóm sinh viên; chỉ chạy sau khi có kết quả Giai đoạn 1. |
| FR-C3 | Xếp theo phạm vi | Giải riêng một chương trình/khóa; lớp ngoài phạm vi bị đóng băng và được bảo vệ, không bị hy sinh nhường chỗ. |
| FR-C4 | Sửa tay kéo-thả | Kéo thẻ buổi học sang ô khác trên lưới; hiển thị trạng thái "chưa lưu"; phải xác nhận trước khi ghi; nếu ô đích xung đột, bắt buộc ghi lý do. |
| FR-C5 | Ghim/bỏ ghim | Buổi đã sửa tay và lưu được ghim, giữ nguyên qua mọi lần giải lại cho tới khi bỏ ghim. |
| FR-C6 | Lưu thời khóa biểu | Ghi giờ đang xếp vào dữ liệu học phần kèm trạng thái từng lớp (đã xếp / có vấn đề / chưa có giờ). |
| FR-C7 | Chốt học phần | Chốt/mở chốt giờ của mọi lớp một học phần; khi chốt, mọi thao tác đổi giờ bị từ chối. |
| FR-C8 | Hoàn tác | Quay lại mốc đã lưu trước đó; mốc được duy trì liên tục qua các phiên làm việc. |

### 3.4. Giám sát, cảnh báo và xuất kết quả

| Mã | Yêu cầu | Mô tả |
|---|---|---|
| FR-D1 | Bộ lọc và hiển thị | Xem theo toàn khoa / chương trình / giảng viên; lọc loại lớp; tìm kiếm; tô màu theo nhiều tiêu chí; hai chế độ xem Lưới (theo tuần) và Bảng (danh sách phẳng). |
| FR-D2 | Hộp thư vấn đề | Cảnh báo trùng giảng viên (kèm buổi bị bỏ lại và người cần liên hệ), nghi trùng lặp dữ liệu, lớp chưa có giờ (gộp theo điều phối viên); vụ đã được chốt hoàn toàn được hạ cấp, thu gọn. |
| FR-D3 | Danh sách chưa xếp được | Liệt kê lớp đã báo giờ nhưng không xếp được; hiển thị từng khung giờ: ô còn trống cho phép xếp ngay, ô đang bận kèm lớp chiếm chỗ. |
| FR-D4 | Bản đồ tuần | Bảng mật độ lớp theo ô (ngày × tiết); bấm ô để nổi bật các buổi tương ứng. |
| FR-D5 | Nhật ký thao tác | Ghi lại mọi thao tác trong phiên để tra cứu. |
| FR-D6 | Xuất kết quả | Xuất Excel chuẩn FATE sau khi lưu TKB; xuất thêm lưới TKB theo định dạng riêng. |

## 4. Ràng buộc nghiệp vụ của bài toán xếp lịch

Đây là phần cốt lõi được chuyển tiếp từ tài liệu phân tích nghiệp vụ; bộ giải phải cài đặt đúng các quy tắc sau.

### 4.1. Ràng buộc cứng (bắt buộc)

| STT | Ràng buộc | Nội dung |
|---|---|---|
| 1 | Trùng giảng viên | Một giảng viên (kể cả đồng giảng) chỉ có mặt tại một buổi tại một thời điểm. |
| 2 | Pool phòng | Số lớp lý thuyết/thực hành đồng thời không vượt pool tương ứng (khai báo qua cấu hình). |
| 3 | Khối ca | Buổi học nằm gọn trong khối ca: sáng và chiều–tối, phân theo cơ sở; không vắt qua giờ nghỉ trưa. |
| 4 | Giới hạn ngày dạy | Không tự xếp ai vào Chủ nhật; thỉnh giảng tối đa đến thứ Bảy, cơ hữu đến thứ Sáu; giờ con người đã chốt trong file vẫn được giữ (chỉ cảnh báo). |
| 5 | Học chung | Cả nhóm cùng giờ, cùng được xếp/không được xếp, chiếm một suất phòng. |

### 4.2. Ràng buộc mềm (tối ưu khi có thể)

Do dữ liệu thực tế chứa các xung đột đã chốt, các quy tắc sau là **mức độ ưu tiên** chứ không phải điều kiện bắt buộc:

1. Tránh trùng giờ nhóm sinh viên (ưu tiên rất cao; miễn cho học chung, lớp song hành cùng học phần, lớp trực tuyến).
2. Một giảng viên không dạy hai cơ sở trong cùng ngày.
3. Gom các buổi cùng cơ sở vào ít ngày nhất; ưu tiên giảm chuyến đi Hòa Lạc trước.
4. Dàn đều số buổi trong tuần.

### 4.3. Thứ tự ưu tiên mục tiêu

Khi không thể thỏa mãn đồng thời mọi mục tiêu, bộ giải lựa chọn theo thứ tự: (1) xếp được nhiều buổi nhất; (2) ít trùng nhóm sinh viên nhất; (3) ít giảng viên phải dạy hai cơ sở trong ngày nhất; (4) ít chuyến đi nhất; (5) lịch dàn đều nhất.

## 5. Yêu cầu phi chức năng

| Mã | Yêu cầu | Mô tả |
|---|---|---|
| NFR-1 | Hiệu năng | Một lần giải hoàn tất trong giới hạn thời gian cấu hình; hết giờ trả về phương án tốt nhất đã tìm được, không treo ứng dụng. |
| NFR-2 | Toàn vẹn dữ liệu | Thao tác phá hủy phải xác nhận; thao tác sinh dữ liệu theo kiểu tất-cả-hoặc-không-có-gì (lỗi giữa chừng không làm hỏng dữ liệu cũ). |
| NFR-3 | Bền vững dữ liệu | Dữ liệu nhập tay được lưu liên tục và tự khôi phục khi khởi động lại; tải lại trang không mất dữ liệu. |
| NFR-4 | Khả năng cấu hình | Lịch tuần, số phòng, giới hạn ngày dạy, khối ca, tham số bộ giải và bộ sinh giờ rảnh đều cấu hình được ngoài mã nguồn; cấu hình sai phải bị phát hiện ngay khi khởi động. |
| NFR-5 | Khả năng kiểm thử | Tách nghiệp vụ khỏi giao tiếp để kiểm thử đơn vị; có kịch bản đo trên dữ liệu thật để kiểm chứng bất biến của nghiệm. |
| NFR-6 | Môi trường vận hành | Chạy cục bộ, không xác thực; kết quả chỉ mang tính tham khảo cho giáo vụ. |
| NFR-7 | Khả năng phục hồi | Hoàn tác về mốc; cảnh báo trước thao tác không thể hoàn tác; nhật ký thao tác. |

## 6. Thiết kế hệ thống đề xuất

### 6.1. Kiến trúc tổng thể

Kiến trúc client–server hai thành phần, chạy trên một máy:

1. **Giao diện web (SPA)** — hiển thị lưới TKB theo tuần, bảng dữ liệu học phần, các form nhập liệu, hộp thư vấn đề; gọi API qua HTTP.
2. **Máy chủ ứng dụng** — tiếp nhận yêu cầu, quản lý trạng thái phiên làm việc, cài đặt quy tắc nghiệp vụ, gọi bộ giải xếp lịch, đọc/ghi file Excel, lưu dữ liệu.

Lý do chọn kiến trúc này: nghiệp vụ nặng về tính toán (bộ giải) và xử lý file (Excel) chạy ổn định ở phía máy chủ; giao diện cần thao tác trực quan (kéo-thả lưới tuần) nên dùng ứng dụng web hiện đại thay vì bảng tính.

### 6.2. Lựa chọn công nghệ

| Thành phần | Công nghệ đề xuất | Lý do chọn |
|---|---|---|
| Giao diện | React + Vite | Hệ sinh thái component phù hợp lưới TKB phức tạp; Vite cho vòng lặp phát triển nhanh. |
| Kiểu dáng | Tailwind CSS + bộ component | Giao diện nhất quán, làm nhanh theo nhận diện thương hiệu. |
| Máy chủ | Python + Flask | Gọn nhẹ, đủ cho ứng dụng nội bộ một máy. |
| Bộ giải | Google OR-Tools (CP-SAT) | Bộ giải ràng buộc trưởng thành, mô hình hóa trực tiếp các quy tắc cứng/mềm ở mục 4. |
| Bảng tính | openpyxl | Đọc/ghi Excel khuôn chuẩn FATE không phụ thuộc cài đặt Office. |
| Kiểm thử | pytest + Vitest | Kiểm thử đơn vị hai phía, khớp ngăn xếp công nghệ. |

### 6.3. Phân chia mô-đun

| Mô-đun | Trách nhiệm |
|---|---|
| Giao diện — các màn | Chọn vai trò; TKB (lưới/bảng); dữ liệu học phần; nộp khung giờ; giờ rảnh giảng viên; nhật ký. |
| Tầng API | Nhóm endpoint theo nghiệp vụ: trạng thái/dữ liệu, nhập–xuất Excel, nhập tay, giải, điều chỉnh, chốt, hoàn tác. |
| Tầng nghiệp vụ | Quy tắc thuần không phụ thuộc HTTP: phạm vi xếp, nhóm sinh viên, học chung, ghim/chốt, hoàn tác, hợp nhất dòng Excel. |
| Bộ giải | Mô hình hóa bài toán thành ràng buộc CP-SAT, hai giai đoạn, đọc thuộc tính lớp. |
| Xử lý file | Đọc file Excel kế hoạch giảng dạy, kiểm tra chất lượng dữ liệu, xuất kết quả. |
| Lưu trữ | Snapshot dữ liệu nhập tay, mốc hoàn tác, tệp cấu hình — dạng JSON tại máy. |

### 6.4. Mô hình dữ liệu khái niệm

| Thực thể | Thuộc tính chính | Quan hệ |
|---|---|---|
| Giảng viên | mã, họ tên, đơn vị, học hàm/vị, email, SĐT, loại, giờ rảnh theo tiết | dạy nhiều lớp |
| Học phần | mã, tên, số tín chỉ | mở nhiều lớp |
| Lớp học phần | mã, học phần, giảng viên, thứ/tiết (hoặc "tự xếp"), chương trình, khóa, hình thức, loại phòng, số sinh viên, trạng thái | thuộc một học phần, một giảng viên chính |
| Khung giờ đã báo | lớp, thứ, tiết đầu, tiết cuối, người nộp | thuộc một lớp |
| Nhóm học chung | danh sách lớp thành viên | gộp nhiều lớp |
| Nhật ký thao tác | thời điểm, loại thao tác, chi tiết | — |

### 6.5. Thiết kế giao tiếp giữa các thành phần

Các nhóm API cần cung cấp (chi tiết endpoint cụ thể hóa khi triển khai):

| Nhóm API | Nghiệp vụ |
|---|---|
| Trạng thái và dữ liệu | Xem tình trạng, lấy bộ dữ liệu hiện có. |
| Nhập/xuất Excel | Xem trước, nạp chính thức, tải file danh sách vấn đề, xuất kết quả. |
| Nhập tay | Giảng viên, học phần, lớp, học chung, bỏ qua lớp, tự động sinh giờ rảnh. |
| Giải | Kích hoạt Giai đoạn 1, Giai đoạn 2, lấy kết quả. |
| Điều chỉnh | Kéo-thả, bỏ ghi đè, lưu TKB, chốt/bỏ chốt. |
| Phục hồi | Hoàn tác, nhật ký. |

### 6.6. Thiết kế giao diện người dùng

| Màn | Nội dung chính |
|---|---|
| Chọn vai trò | Toàn quyền (giáo vụ) hoặc chỉ xem; ghi nhớ lựa chọn trên trình duyệt. |
| Thời khóa biểu | Màn trung tâm; thanh tiến trình ba bước (Thu giờ — Giải thỉnh giảng — Ghép cơ hữu); lưới tuần kéo-thả được ở chế độ toàn màn hình; hộp thư vấn đề; bản đồ tuần. |
| Dữ liệu học phần | Bảng phản chiếu Excel gốc; nhập tay, nhập/xuất file, xoá giờ, bỏ qua lớp, bắt đầu học kỳ mới. |
| Chuẩn bị dữ liệu | Nộp khung giờ cho lớp thỉnh giảng; khai báo giờ rảnh giảng viên kèm đề xuất tự động. |
| Nhật ký & bản lưu | Lịch sử thao tác phiên làm việc. |

### 6.7. Cơ chế lưu trữ và cấu hình

- **Dữ liệu phiên** (dữ liệu nhập tay, mốc hoàn tác) lưu tại máy dưới dạng tệp JSON, ghi sau mỗi thao tác, tự nạp khi khởi động; kết quả giải không bắt buộc lưu qua phiên.
- **Cấu hình** chứa: lịch tuần (ngày, số tiết), pool phòng theo loại, giới hạn ngày dạy theo loại giảng viên, khối ca theo cơ sở, tham số bộ giải (giới hạn thời gian, số luồng), tham số bộ sinh giờ rảnh. Thiếu nhóm cấu hình dùng giá trị mặc định; cấu hình sai khiến hệ thống từ chối khởi động kèm thông báo lỗi.

## 7. Kế hoạch triển khai và nghiệm thu

### 7.1. Lộ trình phát triển theo giai đoạn

| Giai đoạn | Phạm vi | Kết quả bàn giao |
|---|---|---|
| GĐ 0 — Phân tích | Hoàn tất hai tài liệu nghiệp vụ đầu vào (mục 1.5). | Ràng buộc và quy trình được thống nhất. |
| GĐ 1 — Nòng cốt | Quản lý dữ liệu học phần (FR-A1–A5), nộp khung giờ (FR-B1, B4), giải hai giai đoạn (FR-C1–C2), lưới xem TKB (FR-D1). | Có thể nạp file thật và ra lịch tự động. |
| GĐ 2 — Bán tự động | Sửa tay, ghim, lưu TKB, chốt, hoàn tác (FR-C4–C8), hộp thư vấn đề (FR-D2–D3), nhật ký (FR-D5), xuất kết quả (FR-D6). | Vòng lặp nạp → giải → sửa → xuất khép kín. |
| GĐ 3 — Mở rộng | Xếp theo phạm vi, học chung, bỏ qua lớp (FR-A8–A9, FR-C3), bản đồ tuần (FR-D4), xoá giờ hàng loạt (FR-A6), học kỳ mới (FR-A7). | Vận hành được nhiều chương trình song song. |
| GĐ 4 — Trợ năng | Tự động khai giờ rảnh (FR-B3), tinh chỉnh hiệu năng và trải nghiệm. | Giảm thao tác nhập liệu thủ công. |

### 7.2. Tiêu chí nghiệm thu

1. Mọi FR ở giai đoạn tương ứng hoạt động đúng mô tả; không có xung đột cứng trong nghiệm của bộ giải.
2. Kịch bản đo trên dữ liệu thật: lớp ngoài phạm vi không bị xê dịch; không phát sinh thêm trùng nhóm sinh viên tránh được; không vượt pool phòng.
3. Toàn bộ thao tác phá hủy có xác nhận; hoàn tác hoạt động đúng.
4. File xuất ra nạp lại được mà không mất hoặc sai dữ liệu.
5. Bài kiểm thử tự động hai phía chạy xanh.

### 7.3. Chiến lược kiểm thử

- **Đơn vị:** kiểm thử tầng nghiệp vụ và bộ giải bằng dữ liệu nhỏ, có thể lặp lại.
- **Đo bất biến trên dữ liệu thật:** kịch bản chạy độc lập giao diện, đối chiếu nghiệm với ba bất biến (phạm vi, trùng nhóm sinh viên, pool phòng).
- **Giao diện:** kiểm thử component chính; kịch bản thủ công theo luồng nghiệp vụ ở mục 2.5 cho từng vai trò.

## 8. Phân tích rủi ro

| Rủi ro | Tác động | Biện pháp giảm thiểu |
|---|---|---|
| Bài toán NP-hard, không tìm nghiệm trong thời hạn | Trễ tiến độ làm việc | Giới hạn thời gian và lấy nghiệm tốt nhất; chiến lược hai giai đoạn chia nhỏ bài toán. |
| Dữ liệu Excel gốc không sạch (hai nguồn giờ lệch, dòng trùng) | Lịch sai từ đầu vào | Bước chuẩn hoá bắt buộc, xem trước khi nạp, liệt kê rõ dữ liệu bất thường. |
| Dữ liệu thật có sẵn xung đột đã chốt | Không thể cấm tuyệt đối | Thiết kế ràng buộc mềm theo thứ tự ưu tiên; hạ cấp vấn đề đã chốt. |
| Mất dữ liệu nhập tay do tắt máy | Mất công sức nhập liệu | Snapshot sau mỗi thao tác, tự khôi phục khi khởi động. |
| Người dùng thao tác không thể hoàn tác | Mất dữ liệu không phục hồi | Xác nhận bắt buộc, hoàn tác về mốc, nhật ký thao tác. |
| Nâng cấp thư viện bộ giải làm thay đổi hành vi | Nghiệm lệch không được phát hiện | Khóa/chặn dưới phiên bản, chạy lại kịch bản đo bất biến sau mỗi nâng cấp. |

## 9. Hạn chế đã biết và hướng phát triển tương lai

Hạn chế được chấp nhận trong thiết kế hiện tại:

1. Quản lý phòng theo pool, chưa gán phòng cụ thể và sức chứa từng phòng — việc này thuộc bước gán phòng của Phòng Đào tạo.
2. Trùng nhóm sinh viên là ràng buộc mềm do dữ liệu thực tế đã có xung đột chốt sẵn.
3. Không có phân quyền tài khoản; vai trò chỉ là lựa chọn trên trình duyệt.

Hướng phát triển sau khi bàn giao: gán phòng cụ thể kèm sức chứa; nâng trùng nhóm sinh viên thành ràng buộc cứng khi dữ liệu đầu vào sạch; lưu kết quả giải theo phiên; đa người dùng và phân quyền.
