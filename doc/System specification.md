# ĐẶC TẢ HỆ THỐNG VJU-CALENDAR

**Hệ thống hỗ trợ xếp thời khóa biểu tự động — Trường Đại học Việt Nhật (VJU)**

| Thuộc tính | Giá trị |
|---|---|
| Tên hệ thống | VJU-Calendar |
| Phiên bản tài liệu | 2.4 |
| Ngày cập nhật | 25/11/2026 |
| Bản chất tài liệu | Đặc tả yêu cầu và thiết kế, có đối chiếu với bản triển khai hiện tại |

> Các mục `FR` và `NFR` mô tả yêu cầu; mục 7 nêu cách nghiệm thu. Phụ lục A ghi các giới hạn đã xác định qua đối chiếu mã nguồn, không thay thế kết quả nghiệm thu.

## 1. Giới thiệu

### 1.1. Mục đích tài liệu

Mô tả yêu cầu chức năng, yêu cầu phi chức năng, ràng buộc nghiệp vụ và lý do chọn thiết kế của VJU-Calendar. Tài liệu dùng để tiếp nhận dự án, đối chiếu với bản triển khai hiện tại và xác định tiêu chí nghiệm thu.

### 1.2. Phạm vi hệ thống

VJU-Calendar là công cụ phần mềm hỗ trợ Phòng Đào tạo và giáo vụ khoa xây dựng thời khóa biểu (TKB) học kỳ, với các năng lực cần có:

- Tự động xếp lịch bằng bộ giải ràng buộc, theo chiến lược hai giai đoạn: xếp lớp giảng viên thỉnh giảng trước, ghép lớp giảng viên cơ hữu sau.
- Hỗ trợ điều chỉnh bán tự động: kéo-thả, ghim, chốt lịch; cảnh báo xung đột tức thời.
- Trao đổi dữ liệu với file Excel kế hoạch giảng dạy (nhập có kiểm tra, xuất hoàn chỉnh).

Ngoài phạm vi bản hiện tại: phân quyền theo tài khoản, đối chiếu lịch/phòng giữa các khoa trên toàn trường, gán phòng theo tên, tính số lớp cần mở theo sức chứa từng phòng, quản lý đăng ký môn của sinh viên, xếp lịch thi và tích hợp hệ thống quản lý đào tạo khác.

**Phạm vi phiên bản tiếp theo:** đưa ứng dụng lên máy chủ web (mục 6.8), đăng nhập bằng tài khoản VJU và kiểm soát truy cập theo vai trò, phạm vi được gán (mục 3.5). Bản hiện tại vẫn chạy cục bộ và dùng vai trò mô phỏng.

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
| Quy trình nghiệp vụ xếp TKB | Vai trò GĐCT, ĐPCT, Trợ lý khoa và giảng viên cơ hữu; JLE/Phòng Đào tạo điều phối nhưng không có vai trò đăng nhập riêng. |

## 2. Miêu tả tổng thể

### 2.1. Bối cảnh và vấn đề

Mỗi học kỳ, trường phải xếp lịch cho hàng trăm lớp học phần, đồng thời cân đối: giờ rảnh của giảng viên thỉnh giảng, lịch của các nhóm sinh viên, số lượng phòng theo loại tại hai cơ sở (Hòa Lạc, Mỹ Đình) và các thỏa thuận giờ đã chốt với giảng viên ngoài trường. Cách làm thủ công dễ phát sinh trùng lịch, khó kiểm tra chéo giữa các chương trình và tiêu tốn nhiều thời gian công.

### 2.2. Mục tiêu và tiêu chí thành công

**Mục tiêu:** (1) tự động hóa tính toán xếp lịch; (2) giữ quyền quyết định cuối cùng cho con người thông qua chế độ bán tự động; (3) giảm sai sót và thời gian làm việc nhờ trao đổi trực tiếp với file Excel kế hoạch giảng dạy.

**Tiêu chí thành công** (đo được khi nghiệm thu):

1. Mỗi giai đoạn giải tuân theo giới hạn thời gian của bộ giải (cấu hình mẫu: 30 giây); phản hồi theo NFR-1.
2. Kết quả giải không chứa xung đột cứng: không trùng giảng viên, không vượt pool phòng, buổi học luôn nằm gọn trong khối ca.
3. Mọi thao tác phá hủy dữ liệu đều có bước xác nhận. Việc hoàn tác được kiểm tra riêng theo phạm vi của FR-C8.
4. File xuất theo khuôn FATE có thể nạp lại; file Excel lưới TKB phục vụ tra cứu, không phải đầu vào nhập liệu.
5. Cảnh báo xung đột hiển thị ngay khi người dùng sửa tay.

### 2.3. Bên liên quan

| Bên liên quan | Mối quan tâm |
|---|---|
| GĐCT | Quản lý giảng viên thỉnh giảng và xếp TKB trong CTĐT phụ trách. |
| ĐPCT | Quản lý giảng viên thỉnh giảng trong CTĐT phụ trách; không mặc định có quyền xếp lịch. |
| Trợ lý khoa | Thao tác toàn trường; quản lý giảng viên thỉnh giảng, cập nhật giờ rảnh cơ hữu và xếp lịch thay GĐCT khi cần. |
| Giảng viên cơ hữu | Tự khai giờ rảnh. |
| JLE / Phòng Đào tạo | Điều phối nghiệp vụ; không có vai trò đăng nhập riêng theo yêu cầu hiện tại. |
| Giảng viên | Không bị xếp trùng giờ, không dạy hai cơ sở trong một ngày, lịch gọn gàng. |
| Sinh viên | Người hưởng lợi cuối; không bị hai môn chùng giờ trong cùng nhóm. |
| Nhà phát triển | Cấu trúc rõ ràng, tách nghiệp vụ khỏi giao tiếp, dễ kiểm thử. |

### 2.4. Giả định và ràng buộc của dự án

- Bản hiện tại chạy cục bộ trên máy giáo vụ, không cần đăng nhập hoặc kết nối ra Internet. Bản có đăng nhập cần kết nối được tới hệ thống xác thực của VJU để đăng nhập; không giả định đăng nhập hoàn toàn ngoại tuyến.
- Dữ liệu đầu vào chính là file Excel kế hoạch giảng dạy của trường; hệ thống không thể yêu cầu thay đổi cách nhập liệu hiện hành.
- Dữ liệu thực tế đã chứa một số xung đột do con người chốt sẵn; hệ thống phải chấp nhận tồn tại chúng thay vì cấm tuyệt đối.
- Kết quả xếp lịch mang tính tham khảo; quyết định cuối cùng thuộc giáo vụ.

### 2.5. Luồng nghiệp vụ tổng thể

Trình tự sử dụng chính mà hệ thống phải phục vụ:

1. **Nạp dữ liệu** — luồng chuẩn bị dữ liệu hỗ trợ nạp Excel hoặc nhập tay. Yêu cầu nghiệp vụ chưa chỉ định vai trò thực hiện; màn nhập/sửa học phần hiện không được mở trong luồng chọn vai trò mô phỏng.
2. **Chuẩn bị giờ** — GĐCT, ĐPCT hoặc Trợ lý khoa nhập giờ có thể dạy của giảng viên thỉnh giảng; giảng viên cơ hữu tự khai giờ rảnh, Trợ lý khoa có thể nhập thay.
3. **Giải Giai đoạn 1** — hệ thống xếp các lớp thỉnh giảng vào khung giờ đã báo.
4. **Giải Giai đoạn 2** — hệ thống ghép các lớp cơ hữu vào chỗ còn trống sau khi đã giải Giai đoạn 1 cho cùng phạm vi.
5. **Tinh chỉnh** — GĐCT xếp trong CTĐT phụ trách; Trợ lý khoa có thể xếp thay trên phạm vi toàn trường.
6. **Lưu và bàn giao** — ghi giờ đã duyệt vào dữ liệu học phần; xuất FATE để bàn giao dữ liệu hoặc xuất lưới TKB để tra cứu.

Phạm vi toàn trường của Trợ lý khoa là phạm vi thao tác trên bộ dữ liệu đang nạp, không đồng nghĩa với việc hệ thống có lịch của mọi khoa.

## 3. Yêu cầu chức năng

Yêu cầu chức năng được mã hóa `FR-x`, nhóm theo năm cụm; diễn đạt dưới dạng "hệ thống phải".

### 3.1. Quản lý dữ liệu học phần

Bảng dữ liệu học phần là nguồn dữ liệu duy nhất của toàn hệ thống, phản chiếu cấu trúc file Excel kế hoạch giảng dạy gốc.

| Mã | Yêu cầu | Mô tả |
|---|---|---|
| FR-A1 | Quản lý giảng viên | GĐCT, ĐPCT và Trợ lý khoa được mời/cập nhật hồ sơ và giờ có thể dạy của giảng viên thỉnh giảng. Giảng viên cơ hữu tự khai giờ rảnh; Trợ lý khoa có thể cập nhật thay. |
| FR-A2 | Quản lý học phần | Thêm/sửa học phần: mã, tên, số tín chỉ. Người được phép thực hiện chưa được phân công trong yêu cầu hiện tại. |
| FR-A3 | Quản lý lớp học phần | Tạo lớp từ giảng viên + học phần; khai Thứ/Tiết cố định hoặc đánh dấu "để hệ thống tự xếp". Người được phép thực hiện chưa được phân công trong yêu cầu hiện tại. |
| FR-A4 | Nhập Excel hai bước | Bước xem trước: đọc và chuẩn hoá file nhưng **chưa thay đổi bộ dữ liệu đang làm việc**; liệt kê vấn đề như giờ ghi không nhất quán, dòng trùng hoặc lớp thiếu giảng viên. Có thể tải danh sách lỗi `.xlsx` để sửa file nguồn. Bước nạp: xác nhận **Gộp thêm** vào bộ đang có hoặc **Thay thế** bộ đang có. Vai trò thực hiện chưa được chốt; xem Phụ lục A. |
| FR-A5 | Xuất Excel chuẩn | Xuất dữ liệu học phần theo khuôn FATE, cho phép chọn toàn bộ hoặc chỉ các lớp đang hiển thị theo bộ lọc. File FATE dùng để bàn giao dữ liệu và có thể nạp lại. |
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
| FR-C2 | Giải Giai đoạn 2 | Ghép lớp cơ hữu vào chỗ trống, né kết quả Giai đoạn 1 về giảng viên, pool phòng và nhóm sinh viên theo mục 4. Chỉ chạy khi đã giải Giai đoạn 1 cho đúng phạm vi đang chọn; nếu đổi phạm vi, phải giải lại Giai đoạn 1. |
| FR-C3 | Xếp theo phạm vi | Giải riêng một chương trình/khóa; lớp ngoài phạm vi bị đóng băng và được bảo vệ, không bị hy sinh nhường chỗ. |
| FR-C4 | Sửa tay kéo-thả | Kéo thẻ buổi học sang ô khác trên lưới; hiển thị trạng thái "chưa lưu"; phải xác nhận trước khi ghi; nếu ô đích xung đột, bắt buộc ghi lý do. |
| FR-C5 | Ghim/bỏ ghim | Buổi đã sửa tay và lưu được ghim, giữ nguyên qua mọi lần giải lại cho tới khi bỏ ghim. |
| FR-C6 | Lưu thời khóa biểu | Ghi giờ đang xếp vào dữ liệu học phần kèm trạng thái từng lớp (đã xếp / có vấn đề / chưa có giờ). |
| FR-C7 | Chốt học phần | Chốt/mở chốt giờ của mọi lớp một học phần; khi chốt, mọi thao tác đổi giờ bị từ chối. |
| FR-C8 | Hoàn tác | «Hủy thay đổi» đưa bộ dữ liệu và lịch về **một mốc duy nhất**, tạo sau lần nạp Excel hoặc lần lưu TKB gần nhất. Tạo mốc mới thay mốc cũ; mốc được nạp lại khi khởi động ứng dụng và không phải lịch sử hoàn tác từng thao tác. |

### 3.4. Giám sát, cảnh báo và xuất kết quả

| Mã | Yêu cầu | Mô tả |
|---|---|---|
| FR-D1 | Bộ lọc và hiển thị | Xem theo toàn khoa / chương trình / giảng viên; lọc loại lớp; tìm kiếm; tô màu theo nhiều tiêu chí; hai chế độ xem Lưới (theo tuần) và Bảng (danh sách phẳng). |
| FR-D2 | Hộp thư vấn đề | Cảnh báo trùng giảng viên (kèm buổi bị bỏ lại và người cần liên hệ), nghi trùng lặp dữ liệu, lớp chưa có giờ (gộp theo điều phối viên); vụ đã được chốt hoàn toàn được hạ cấp, thu gọn. |
| FR-D3 | Danh sách chưa xếp được | Liệt kê lớp đã báo giờ nhưng không xếp được; hiển thị từng khung giờ: ô còn trống cho phép xếp ngay, ô đang bận kèm lớp chiếm chỗ. |
| FR-D4 | Bản đồ tuần | Bảng mật độ lớp theo ô (ngày × tiết); bấm ô để nổi bật các buổi tương ứng. |
| FR-D5 | Nhật ký thao tác | Ghi lại các thao tác trong phiên giao diện để tra cứu. Không yêu cầu lưu qua lần tải lại trang; xem Phụ lục A về phạm vi ghi nhận hiện tại. |
| FR-D6 | Xuất kết quả | Để đưa giờ vừa xếp vào file FATE, lưu TKB trước rồi xuất dữ liệu học phần theo FR-A5. Có thể xuất lưới TKB đang hiển thị thành file `.xlsx` riêng; file này không dùng để nạp lại theo FR-A4. |

### 3.5. Đăng nhập và phân quyền theo vai trò

Đây là yêu cầu cho **phiên bản tiếp theo**, chưa có trong bản đang chạy. Hệ thống xác thực của VJU xác minh danh tính; VJU-Calendar quyết định tài khoản được sử dụng chức năng và dữ liệu nào. Nhà cung cấp và giao thức tích hợp sẽ được xác nhận với bộ phận IT của VJU.

| Mã | Yêu cầu | Mô tả |
|---|---|---|
| FR-E1 | Đăng nhập và đăng xuất bằng tài khoản VJU | Người dùng đăng nhập qua hệ thống xác thực của VJU. VJU-Calendar không thu thập, lưu trữ hoặc đặt lại mật khẩu VJU. Trong luồng đăng nhập, sau khi VJU xác thực thành công, máy chủ lấy vai trò và phạm vi đã gán cho tài khoản trước khi tạo phiên ứng dụng. Người dùng không phải chọn vai trò. Nếu chưa được cấp quyền thì không tạo phiên; khi đăng xuất hoặc phiên hết hạn thì phiên đó không còn truy cập được dữ liệu nội bộ. |
| FR-E2 | Kiểm soát truy cập theo vai trò và phạm vi | Máy chủ kiểm tra quyền ở mỗi yêu cầu truy cập dữ liệu hoặc thực hiện thao tác nội bộ. Vai trò và phạm vi lấy từ quyền đã gán cho tài khoản, không do người dùng tự chọn. GĐCT chỉ xếp lịch cho CTĐT được giao; ĐPCT không có quyền xếp lịch; Trợ lý khoa có thể xếp lịch trên bộ dữ liệu được phép quản lý; giảng viên cơ hữu chỉ tự khai giờ cho hồ sơ của mình; vai trò Xem thôi chỉ tra cứu dữ liệu được phép. Việc ẩn nút trên giao diện không thay thế kiểm tra ở máy chủ. |
| FR-E3 | Gán và thu hồi quyền trong ứng dụng (đề xuất) | Nếu triển khai màn quản trị, người được giao quản trị có thể gán, thay đổi hoặc thu hồi vai trò và phạm vi của tài khoản VJU trong VJU-Calendar. Thao tác này không quản lý mật khẩu hay khóa tài khoản tại VJU. Phạm vi của màn quản trị và người thực hiện cần được chốt trước khi triển khai. |

Quyền nhập Excel và sửa dữ liệu học phần vẫn chưa được phân công. Không tự động cấp các quyền này cho bất kỳ vai trò nào chỉ vì tài khoản đã đăng nhập.

## 4. Ràng buộc nghiệp vụ của bài toán xếp lịch

Đây là phần cốt lõi được chuyển tiếp từ tài liệu phân tích nghiệp vụ; bộ giải phải cài đặt đúng các quy tắc sau.

**Phạm vi kiểm tra phòng:** quy trình nghiệp vụ mô tả rằng khoa không đối chiếu trùng phòng với lịch của các khoa khác trong bước xếp TKB. Trong ứng dụng, bộ giải vẫn kiểm giới hạn tổng số suất **lý thuyết (LT)** và **thực hành (LAB)** cho các lớp được tính trong mô hình. Kiểm giới hạn này không có nghĩa là đã chọn được phòng cụ thể hay đã kiểm lịch trên toàn trường. Việc lập phương án mở lớp theo sức chứa và gán phòng cụ thể không thuộc bản hiện tại.

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
| NFR-1 | Hiệu năng | Mỗi giai đoạn giải dùng giới hạn thời gian cấu hình. Khi hết giờ và đã có nghiệm khả thi, trả về phương án tốt nhất đã tìm được, không khẳng định tối ưu. Nếu chưa có nghiệm khả thi, thông báo rõ thay vì trả về lịch như thể đã giải thành công. Đây là tiêu chí cần kiểm chứng khi nghiệm thu. |
| NFR-2 | Toàn vẹn dữ liệu | Thao tác phá hủy phải xác nhận; thao tác sinh dữ liệu theo kiểu tất-cả-hoặc-không-có-gì (lỗi giữa chừng không làm hỏng dữ liệu cũ). |
| NFR-3 | Bền vững dữ liệu | Dữ liệu nhập tay được lưu liên tục và tự khôi phục khi khởi động lại; tải lại trang không mất dữ liệu. |
| NFR-4 | Khả năng cấu hình | Lịch tuần, số phòng, giới hạn ngày dạy, khối ca, tham số bộ giải và bộ sinh giờ rảnh đều cấu hình được ngoài mã nguồn; cấu hình sai phải bị phát hiện ngay khi khởi động. |
| NFR-5 | Khả năng kiểm thử | Tách nghiệp vụ khỏi giao tiếp để kiểm thử đơn vị; có kịch bản đo trên dữ liệu thật để kiểm chứng bất biến của nghiệm. |
| NFR-6 | Môi trường vận hành | Bản hiện tại chạy cục bộ, không xác thực. Phiên bản tiếp theo phục vụ người dùng qua URL HTTPS theo mục 6.8 và cần kết nối tới hệ thống xác thực của VJU. Nếu không xác thực được, không tạo phiên đăng nhập mới và không dùng vai trò mô phỏng để truy cập dữ liệu nội bộ. Kết quả xếp lịch chỉ mang tính tham khảo cho giáo vụ. |
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
| Cơ sở dữ liệu (phiên bản tiếp theo) | MySQL 8.0 | Lưu dữ liệu nghiệp vụ và quyền tài khoản; dùng giao dịch để ghi nhất quán các thay đổi liên quan. |
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

**Bổ sung cho phiên bản dùng MySQL 8.0:**

| Thực thể | Thuộc tính chính | Quan hệ |
|---|---|---|
| Tài khoản VJU | Định danh do hệ thống xác thực VJU trả về; không lưu mật khẩu VJU | Có thể liên kết với hồ sơ giảng viên tương ứng, dùng để giới hạn quyền tự khai giờ rảnh. |
| Vai trò | GĐCT, ĐPCT, Trợ lý khoa, Giảng viên cơ hữu, Xem thôi | Tập vai trò giữ nguyên; chức năng và giới hạn theo FR-E2. |
| Gán quyền | Tài khoản, vai trò, phạm vi dữ liệu được phép | Liên kết tài khoản với vai trò và phạm vi đã cấp, ví dụ CTĐT mà GĐCT phụ trách. |

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
| Xác thực và phân quyền (phiên bản tiếp theo) | Đăng nhập qua VJU, kết thúc phiên ứng dụng và kiểm tra quyền trên các API nội bộ. |

### 6.6. Thiết kế giao diện người dùng

| Màn | Nội dung chính |
|---|---|
| Chọn vai trò | GĐCT, ĐPCT, Trợ lý khoa, Giảng viên cơ hữu hoặc Xem thôi; ghi nhớ lựa chọn trên trình duyệt. Đây là vai trò mô phỏng giao diện, không phải đăng nhập hay phân quyền API. |
| Thời khóa biểu | Màn trung tâm; thanh tiến trình ba bước (Thu giờ — Giải thỉnh giảng — Ghép cơ hữu); lưới tuần kéo-thả được ở chế độ toàn màn hình; hộp thư vấn đề; bản đồ tuần. |
| Dữ liệu học phần | Bảng phản chiếu Excel gốc; nhập tay, nhập/xuất file, xoá giờ, bỏ qua lớp, bắt đầu học kỳ mới. Màn này hiện không được mở trong luồng chọn vai trò mô phỏng. |
| Chuẩn bị dữ liệu | Nộp khung giờ cho lớp thỉnh giảng; khai báo giờ rảnh giảng viên kèm đề xuất tự động. |
| Nhật ký & bản lưu | Nhật ký phiên giao diện; mục «Lịch đã lưu» mới là màn chờ, chưa hỗ trợ lưu và mở nhiều phương án. |

| Vai trò mô phỏng | Nghiệp vụ trên giao diện |
|---|---|
| GĐCT | Quản lý giảng viên thỉnh giảng và xếp lịch trong CTĐT được chọn. |
| ĐPCT | Quản lý hồ sơ và giờ có thể dạy của giảng viên thỉnh giảng; không xếp lịch. |
| Trợ lý khoa | Quản lý giảng viên thỉnh giảng, nhập giờ rảnh thay giảng viên cơ hữu, xếp lịch trên bộ dữ liệu đang nạp. |
| Giảng viên cơ hữu | Khai báo giờ rảnh cho hồ sơ giảng viên được chọn trong bản mô phỏng; không xác minh danh tính. |
| Xem thôi | Tra cứu TKB và nhật ký; không sửa lịch hoặc dữ liệu. |

**Phiên bản có đăng nhập:** bỏ màn chọn vai trò. Khi đăng nhập bằng tài khoản VJU, ứng dụng xác định sẵn vai trò và phạm vi của tài khoản rồi đưa người dùng thẳng vào giao diện tương ứng. Vai trò chỉ hiển thị để người dùng biết, không có bước chọn hoặc tự đổi vai trò. Giữ nguyên năm vai trò nghiệp vụ: **GĐCT, ĐPCT, Trợ lý khoa, Giảng viên cơ hữu và Xem thôi**. Giao diện có thao tác «Đăng xuất»; nếu tài khoản chưa được cấp quyền thì thông báo rõ và không mở dữ liệu nội bộ.

### 6.7. Cơ chế lưu trữ và cấu hình

**Bản hiện tại — snapshot JSON:**

- **Dữ liệu đang làm việc:** snapshot JSON lưu dữ liệu học phần và các giờ đã ghi vào đó. Khi khởi động máy chủ, ứng dụng đọc snapshot và dựng lại lịch ban đầu từ giờ đã lưu.
- **Mốc hoàn tác:** một tệp JSON riêng được ghi khi nạp Excel hoặc lưu TKB, không ghi sau mọi thao tác. Mốc có thể dùng sau khi khởi động lại; đây không phải thư viện phương án.
- **Kết quả giải đang làm:** giữ trong bộ nhớ máy chủ; F5 có thể lấy lại kết quả khi máy chủ vẫn chạy. Khởi động lại máy chủ không tự nạp nguyên trạng phương án giải đang làm.
- **Nhật ký giao diện:** giữ trong bộ nhớ trình duyệt của trang đang mở; F5 làm mất nhật ký phiên đó.
- **Cấu hình** chứa: lịch tuần (ngày, số tiết), pool phòng theo loại, giới hạn ngày dạy theo loại giảng viên, khối ca theo cơ sở, tham số bộ giải (giới hạn thời gian, số luồng), tham số bộ sinh giờ rảnh. Thiếu nhóm cấu hình dùng giá trị mặc định; cấu hình sai khiến hệ thống từ chối khởi động kèm thông báo lỗi.

**Phiên bản tiếp theo — MySQL 8.0:**

- **Dữ liệu lưu lâu dài:** MySQL là nguồn dữ liệu chính cho CTĐT, giảng viên, học phần, lớp học phần, giờ rảnh, giờ học đã lưu, trạng thái ghim/chốt, nhóm học chung, mốc hoàn tác và quyền gán cho tài khoản VJU. File FATE vẫn dùng để nhập/xuất, không thay thế cơ sở dữ liệu.
- **Dữ liệu không bắt buộc lưu vào MySQL:** cấu hình lịch và bộ giải vẫn quản lý ngoài cơ sở dữ liệu; bản xem trước Excel, kết quả giải chưa lưu và nhật ký phiên giao diện có thể giữ tạm, không yêu cầu khôi phục sau khi khởi động lại.
- **Toàn vẹn dữ liệu:** dùng `InnoDB` và `utf8mb4`; dùng khóa ngoại và ràng buộc duy nhất cho các quan hệ, định danh phù hợp. Nạp Excel chính thức và lưu TKB phải ghi dữ liệu liên quan cùng mốc hoàn tác trong một giao dịch; nếu ghi thất bại, giữ nguyên trạng thái trước thao tác.
- **Kết nối và phục hồi:** chỉ backend kết nối trực tiếp với MySQL, dùng tài khoản có quyền tối thiểu; thông tin kết nối không lưu trong mã nguồn. Có quy trình sao lưu và khôi phục dữ liệu nghiệp vụ lẫn quyền đã cấp. Khi chuyển từ snapshot JSON, giữ bản gốc và đối chiếu số bản ghi, giờ đã lưu và các liên kết trước khi dùng MySQL làm nguồn chính.

Mục này chỉ đặc tả thiết kế lưu trữ; chưa quy định sơ đồ bảng, script SQL hay công cụ chuyển dữ liệu.

### 6.8. Triển khai web và vận hành

Đây là phương án cho **phiên bản tiếp theo**, không phải mô tả môi trường đang chạy.

- **Truy cập:** người dùng mở URL của ứng dụng qua trình duyệt bằng HTTPS, không cần chạy ứng dụng trên máy cá nhân. Tên miền, nơi đặt máy chủ và phạm vi truy cập (Internet hoặc chỉ qua mạng nội bộ/VPN của VJU) cần được thống nhất với bộ phận IT của VJU.
- **Thành phần triển khai:** máy chủ web phục vụ giao diện React đã build; backend Flask xử lý API, tích hợp đăng nhập VJU và kiểm tra quyền. MySQL 8.0 chỉ cho backend kết nối trực tiếp, không mở truy cập từ trình duyệt hoặc Internet.
- **Dữ liệu nội bộ:** có URL web không có nghĩa là công khai thời khóa biểu. Chỉ tài khoản VJU đã được cấp quyền mới được truy cập dữ liệu theo vai trò và phạm vi quy định ở mục 3.5. Thông tin kết nối và cấu hình xác thực được quản lý ngoài mã nguồn.

## 7. Kế hoạch triển khai và nghiệm thu

### 7.1. Kế hoạch phát triển ban đầu

Lộ trình dưới đây lưu lại thứ tự phát triển dự kiến, không phải danh sách tính năng đã bàn giao. Xem Phụ lục A để biết các giới hạn hiện tại.

| Giai đoạn | Phạm vi | Kết quả bàn giao |
|---|---|---|
| GĐ 0 — Phân tích | Hoàn tất hai tài liệu nghiệp vụ đầu vào (mục 1.5). | Ràng buộc và quy trình được thống nhất. |
| GĐ 1 — Nòng cốt | Quản lý dữ liệu học phần (FR-A1–A5), nộp khung giờ (FR-B1, B4), giải hai giai đoạn (FR-C1–C2), lưới xem TKB (FR-D1). | Có thể nạp file thật và ra lịch tự động. |
| GĐ 2 — Bán tự động | Sửa tay, ghim, lưu TKB, chốt, hoàn tác (FR-C4–C8), hộp thư vấn đề (FR-D2–D3), nhật ký (FR-D5), xuất kết quả (FR-D6). | Vòng lặp nạp → giải → sửa → xuất khép kín. |
| GĐ 3 — Mở rộng | Xếp theo phạm vi, học chung, bỏ qua lớp (FR-A8–A9, FR-C3), bản đồ tuần (FR-D4), xoá giờ hàng loạt (FR-A6), học kỳ mới (FR-A7). | Vận hành được nhiều chương trình song song. |
| GĐ 4 — Trợ năng | Tự động khai giờ rảnh (FR-B3), tinh chỉnh hiệu năng và trải nghiệm. | Giảm thao tác nhập liệu thủ công. |

### 7.2. Tiêu chí nghiệm thu

Các kịch bản dưới đây là tiêu chí cần kiểm tra, không phải kết quả đã đạt. Nếu một chức năng chưa có đường thao tác cho vai trò phù hợp, ghi nhận giới hạn thay vì coi việc có API là đã nghiệm thu giao diện.

1. **Vai trò:** GĐCT xếp trong CTĐT đã chọn; ĐPCT không có thao tác xếp lịch; Xem thôi không sửa được lịch qua giao diện. Giảng viên cơ hữu chỉ khai giờ rảnh cho hồ sơ được chọn trong bản mô phỏng.
2. **Nhập và xuất Excel:** xem trước không đổi dữ liệu đang làm việc. Gộp file bổ sung giữ các lớp cũ và thêm lớp mới hợp lệ; Thay thế dùng bộ dữ liệu mới sau khi người dùng xác nhận. Xuất FATE rồi nạp vào bộ kiểm thử riêng: đối chiếu ít nhất mã lớp, mã học phần và Thứ/Tiết bắt đầu/Tiết kết thúc của các lớp có giờ. Với FATE theo bộ lọc, kiểm thêm không xuất lớp ngoài bộ lọc.
3. **Phạm vi và ràng buộc:** sau khi giải thỉnh giảng cho CTĐT A, chuyển sang CTĐT B rồi yêu cầu ghép cơ hữu; hệ thống phải yêu cầu giải thỉnh giảng lại cho B. Trên dữ liệu thật, lớp ngoài phạm vi không bị xê dịch; nghiệm của bộ giải không vi phạm ràng buộc cứng. Với trùng nhóm sinh viên, so sánh với lịch đầu vào và kiểm tra các trùng mới có thể tránh được, không đòi hỏi mọi xung đột có sẵn phải biến mất.
4. **Giới hạn thời gian:** kiểm tra riêng trường hợp hết giờ đã có nghiệm khả thi và chưa tìm được nghiệm. Trường hợp đầu trả nghiệm đã tìm được mà không báo là tối ưu; trường hợp sau thông báo rõ chưa có nghiệm, không hiển thị phương án như kết quả thành công.
5. **Xác nhận và hoàn tác:** kiểm cảnh báo/xác nhận khi thay thế dữ liệu, xóa giờ hàng loạt và bắt đầu học kỳ mới. Kiểm «Hủy thay đổi» quay đúng về mốc sau lần nạp Excel hoặc lưu TKB gần nhất. Nạp file hoặc lưu TKB lần nữa thay mốc cũ, nên không dùng nút này để quay về bộ dữ liệu trước lần nạp mới. Với xóa giờ hàng loạt và bắt đầu học kỳ mới, không kỳ vọng hệ thống tạo mốc riêng ngay trước thao tác.
6. **F5 và khởi động lại:** F5 khi máy chủ vẫn chạy phải lấy lại được kết quả giải đang làm. Sau khi khởi động lại máy chủ, kiểm dữ liệu học phần đã lưu, lịch dựng lại từ giờ đã lưu và mốc hoàn tác; không yêu cầu tự phục hồi phương án giải chưa lưu.
7. **Kiểm thử tự động:** bộ kiểm thử backend và frontend phải chạy đạt; ghi lại dữ liệu và cấu hình dùng cho các kịch bản nghiệm thu thực tế.

**Nghiệm thu riêng cho phiên bản có đăng nhập (FR-E1, FR-E2):**

- Tài khoản VJU hợp lệ và đã được cấp quyền vào thẳng giao diện đúng vai trò và phạm vi được gán, không qua màn chọn vai trò. Nếu xác thực thất bại hoặc tài khoản hợp lệ nhưng chưa được cấp quyền, không tạo phiên ứng dụng và không cho đọc hoặc sửa dữ liệu nội bộ.
- Yêu cầu trực tiếp tới API nội bộ khi chưa đăng nhập, đã đăng xuất hoặc phiên hết hạn phải bị từ chối.
- Ngay cả khi gọi API trực tiếp, tài khoản Xem thôi không sửa được lịch, GĐCT của CTĐT A không xếp được lịch cho CTĐT B, và giảng viên cơ hữu không sửa được giờ rảnh của hồ sơ khác.

**Nghiệm thu triển khai web (NFR-6):** từ một máy người dùng trong phạm vi mạng đã thống nhất, mở URL HTTPS mà không cần chạy ứng dụng cục bộ. Giao diện tải được; tài khoản VJU đã được cấp quyền đăng nhập và vào đúng màn theo vai trò, không qua màn chọn vai trò; người chưa đăng nhập không đọc được dữ liệu nội bộ.

### 7.3. Chiến lược kiểm thử

- **Đơn vị:** kiểm thử tầng nghiệp vụ và bộ giải bằng dữ liệu nhỏ, có thể lặp lại.
- **Đo bất biến trên dữ liệu thật:** kịch bản chạy độc lập giao diện, đối chiếu nghiệm với ba bất biến (phạm vi, trùng nhóm sinh viên, pool phòng).
- **Giao diện:** kiểm thử component chính; kịch bản thủ công theo luồng nghiệp vụ ở mục 2.5 cho từng vai trò.

## 8. Phân tích rủi ro

| Rủi ro | Tác động | Biện pháp giảm thiểu |
|---|---|---|
| Bài toán NP-hard, không tìm nghiệm trong thời hạn | Trễ tiến độ làm việc | Chia nhỏ bài toán thành hai giai đoạn, giới hạn thời gian và phân biệt có nghiệm khả thi với chưa có nghiệm. |
| Dữ liệu Excel gốc không sạch (hai nguồn giờ lệch, dòng trùng) | Lịch sai từ đầu vào | Bước chuẩn hoá bắt buộc, xem trước khi nạp, liệt kê rõ dữ liệu bất thường. |
| Dữ liệu thật có sẵn xung đột đã chốt | Không thể cấm tuyệt đối | Thiết kế ràng buộc mềm theo thứ tự ưu tiên; hạ cấp vấn đề đã chốt. |
| Mất dữ liệu nhập tay do tắt máy | Mất công sức nhập liệu | Snapshot sau mỗi thao tác, tự khôi phục khi khởi động. |
| Người dùng thao tác không thể hoàn tác | Mất dữ liệu không phục hồi | Xác nhận trước thao tác phá hủy và nêu rõ giới hạn của mốc hoàn tác; nhật ký không phải bản sao dữ liệu. |
| Nâng cấp thư viện bộ giải làm thay đổi hành vi | Nghiệm lệch không được phát hiện | Khóa/chặn dưới phiên bản, chạy lại kịch bản đo bất biến sau mỗi nâng cấp. |

## 9. Hạn chế đã biết và hướng phát triển tương lai

Hạn chế được chấp nhận trong thiết kế hiện tại:

1. Kiểm pool LT/LAB trên dữ liệu trong mô hình; chưa đối chiếu lịch/phòng toàn trường, gán phòng cụ thể hoặc tính số lớp cần mở theo sức chứa.
2. Trùng nhóm sinh viên là ràng buộc mềm do dữ liệu thực tế đã có xung đột chốt sẵn.
3. Bản hiện tại chưa có đăng nhập VJU hay phân quyền máy chủ; vai trò chỉ là lựa chọn trên trình duyệt. Yêu cầu phiên bản tiếp theo nằm ở mục 3.5.

Các hướng phát triển khác: gán phòng cụ thể kèm sức chứa; nâng trùng nhóm sinh viên thành ràng buộc cứng khi dữ liệu đầu vào sạch; lưu và khôi phục nhiều phương án xếp lịch; hỗ trợ nhiều người dùng làm việc đồng thời.

## Phụ lục A. Hiện trạng triển khai

Bảng dưới đây chỉ liệt kê những chức năng dễ bị hiểu nhầm về phạm vi. Trạng thái dựa trên đối chiếu mã nguồn, không xác nhận đã vượt qua các kịch bản ở mục 7.2.

| Mã FR/NFR | Trạng thái | Giới hạn và hành vi hiện tại |
|---|---|---|
| FR-A2 đến FR-A7 | Có giới hạn | Có xử lý nhập/sửa học phần, lớp và thao tác Excel tại backend; nhập Excel có cả Gộp thêm và Thay thế. Màn Dữ liệu học phần không được mở trong luồng chọn vai trò mô phỏng. Vai trò nghiệp vụ thực hiện chưa được chốt. |
| FR-C2 | Đã có | Ghép cơ hữu yêu cầu kết quả giải thỉnh giảng cho cùng phạm vi. Lịch ban đầu dựng từ file không thay thế cho kết quả giải thỉnh giảng. |
| FR-C6, FR-C8 | Có giới hạn | Lưu TKB ghi giờ vào dữ liệu học phần; hoàn tác quay về một mốc, không có lịch sử nhiều bước. |
| FR-D5 | Có giới hạn | Nhật ký chỉ ghi các sự kiện mà giao diện có ghi nhận; không lưu qua F5 và không phải nhật ký kiểm toán. |
| FR-D6 | Đã có | Có định dạng xuất FATE và định dạng lưới `.xlsx` riêng. Khả năng nhập lại FATE cần kiểm theo mục 7.2. |
| FR-E1, FR-E2 | Chưa triển khai | Đăng nhập VJU và kiểm tra quyền ở máy chủ là yêu cầu cho phiên bản tiếp theo. Bản hiện tại vẫn dùng vai trò mô phỏng. |
| FR-E3 | Đề xuất | Chưa chốt phạm vi màn quản trị quyền trong VJU-Calendar. |
| NFR-1 | Có giới hạn | Bộ giải có giới hạn thời gian cấu hình. Chưa xác nhận đã xử lý rõ trường hợp hết giờ mà không có nghiệm khả thi; đây là điểm cần kiểm tra khi nghiệm thu. |
| NFR-2, NFR-3, NFR-7 (lưu trữ) | Chưa triển khai MySQL | Bản hiện tại vẫn dùng snapshot JSON và tệp mốc hoàn tác riêng; MySQL 8.0 là thiết kế cho phiên bản tiếp theo. |
| NFR-6 (triển khai web) | Chưa triển khai | Bản hiện tại chạy cục bộ; môi trường web HTTPS và phạm vi mạng truy cập chưa được chốt. |
| Không có mã FR riêng | Chưa có | «Lịch đã lưu» mới là màn chờ; chưa có lưu nhiều phương án, so sánh hoặc mở lại từng phương án. |
