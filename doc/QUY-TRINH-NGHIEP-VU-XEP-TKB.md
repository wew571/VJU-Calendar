# Quy trình nghiệp vụ xếp TKB — vai trò và phạm vi

> Phạm vi: quy trình nghiệp vụ xếp thời khóa biểu (vai trò nào làm gì, input/xử lý/
> output từng bước), áp dụng cho N khoa dùng chung phòng. Không bao gồm phân quyền/
> tài khoản đăng nhập và giao diện cụ thể — xem mục 8.

## 1. Vai trò & trách nhiệm

| Vai trò | Phạm vi nghiệp vụ | Trách nhiệm |
|---|---|---|
| **GĐCT** (Giám đốc Chương trình) | Một CTĐT được phân công | Mời giảng viên thỉnh giảng; nhập/cập nhật hồ sơ và giờ có thể dạy của họ; xếp TKB trong CTĐT phụ trách. |
| **ĐPCT** (Điều phối CT) | Một CTĐT được phân công | Mời giảng viên thỉnh giảng; nhập/cập nhật hồ sơ và giờ có thể dạy của họ. Không được mặc định có quyền xếp lịch. |
| **Trợ lý khoa** | Toàn trường | Có thể thực hiện các việc về giảng viên thỉnh giảng; nhập/cập nhật giờ rảnh thay giảng viên cơ hữu; xếp lịch thay GĐCT khi cần, trên phạm vi toàn trường. |
| **Giảng viên cơ hữu** | Hồ sơ giảng viên của chính mình | Tự khai giờ rảnh. |

Mỗi CTĐT có một GĐCT và một ĐPCT. Toàn trường hiện có 9 CTĐT, trong đó 6 CTĐT
thuộc FATE. Các con số này không phải giá trị để mã hóa cứng trong giao diện.

**JLE và Phòng Đào tạo** tham gia điều phối nghiệp vụ nhưng không có vai trò đăng
nhập riêng trong phạm vi yêu cầu hiện tại. Không được suy ra từ nhiệm vụ điều phối
rằng hai đơn vị này có quyền xếp lịch hoặc có màn hình/tài khoản riêng.

Trong màn Chuẩn bị dữ liệu, số nhóm điều phối viên được tính từ các lớp thỉnh giảng
thuộc dữ liệu/phạm vi đang xem. Đây là số nhóm còn việc hoặc có lớp trong dữ liệu,
không phải số CTĐT; số này thay đổi theo dữ liệu.

## 2. Luồng tổng quát

```
[0a] JLE / Phòng Đào tạo: điều phối nghiệp vụ (không phải vai trò đăng nhập riêng)
[0b] (tuỳ chọn, thủ công) Mô phỏng lại TKB kỳ cũ — dựa vào đó fill TKB kỳ mới,
     không tương đồng thì bỏ qua
        │
        ▼
[1] GĐCT + hệ thống: xác định nhu cầu lớp của CTĐT
        │  output: "Môn X cần K lớp"
        ▼
[2] GĐCT / ĐPCT / Trợ lý khoa: mời giảng viên thỉnh giảng, nhập/cập nhật hồ sơ
        │  output: GV → môn → (có thể có) khung giờ
        ▼
[3] GĐCT / ĐPCT / Trợ lý khoa: nhập/cập nhật giờ có thể dạy của GV thỉnh giảng
        │  output: GV + khung giờ đầy đủ
        ▼
[4] GĐCT: xếp TKB CTĐT phụ trách; Trợ lý khoa có thể xếp thay trên toàn trường
        │  output: TKB theo giờ của khoa
        ▼
[5] JLE / Phòng Đào tạo: điều phối các công việc liên quan (không tạo vai trò đăng nhập)
        │
        ▼
   Thời khóa biểu cuối cùng (có phòng) — bảng tổng hợp toàn trường
```

Danh sách phòng ([0a]) cần có sẵn từ sớm — không chỉ để gán phòng ở [5], mà bước [1]
(tính số lớp tối ưu sức chứa) cũng cần dùng dữ liệu sức chứa phòng.

## 3. Chi tiết từng bước

### [0a] Điều phối tài nguyên phòng

JLE và Phòng Đào tạo phối hợp các công việc liên quan tới tài nguyên phòng. Yêu cầu
hiện tại không tạo vai trò đăng nhập riêng cho hai đơn vị này.

### [0b] Mô phỏng lại TKB kỳ cũ (tuỳ chọn, thủ công)

Dựa vào TKB kỳ trước để fill nhanh TKB kỳ mới — so sánh môn/lớp/GV kỳ mới với kỳ cũ,
môn/lớp nào giống thì tái dùng luôn. Không có điểm tương đồng thì bỏ qua, làm mới hoàn
toàn từ [1]. Chỉ là gợi ý điền nhanh, không bắt buộc và không ảnh hưởng kết quả cuối.

### [1] Tính số lớp cần mở

GĐCT cung cấp số SV dự kiến học môn X trong kỳ (gộp cả SV học lại/trượt vào cùng một
tổng, không tách lớp riêng). Hệ thống dùng tổng SV này cùng sức chứa các phòng cùng
loại (không lọc theo khu vực ở bước này — xem mục 6) để tính số lớp K cần mở, theo
nguyên tắc ở mục 5. Kết quả "Môn X cần K lớp" thuộc CTĐT do GĐCT phụ trách.

### [2] Mời và quản lý giảng viên thỉnh giảng

GĐCT, ĐPCT và Trợ lý khoa đều có thể mời GV thỉnh giảng, nhập/cập nhật hồ sơ GV mới
và nhập/cập nhật giờ có thể dạy. GĐCT/ĐPCT thao tác theo nhiệm vụ của CTĐT mình;
Trợ lý khoa có phạm vi thao tác toàn trường. Cùng một hồ sơ GV có thể được dùng ở
nhiều CTĐT; cách gán/quản lý quyền sở hữu hồ sơ dùng chung cần được thống nhất khi
triển khai tài khoản thật.

### [3] Khai báo giờ rảnh

GĐCT, ĐPCT hoặc Trợ lý khoa có thể nhập/cập nhật giờ có thể dạy của GV thỉnh giảng.
Giảng viên cơ hữu tự khai giờ rảnh; Trợ lý khoa có thể nhập/cập nhật thay. Giờ thiếu
được giữ ở trạng thái chờ theo luồng hiện có.

### [4] Xếp TKB

GĐCT xếp TKB trong CTĐT mình phụ trách. Trợ lý khoa có thể xếp lịch thay GĐCT khi
cần, với phạm vi toàn trường. ĐPCT không được mặc định có quyền xếp lịch.

Input: dữ liệu lớp, GV và giờ có thể dạy, gợi ý từ TKB kỳ cũ (từ [0b], nếu có).

Xếp TKB chỉ dựa vào giờ GV rảnh, không xét khu vực/2 cơ sở (xem mục 6); check trùng
theo giảng viên (đủ dữ liệu vì GV thuộc phạm vi khoa). **Không check trùng phòng ở
bước này** — khoa không thấy TKB của khoa khác, mà phòng là tài nguyên dùng chung
N khoa. Hoàn thiện xếp thời khóa biểu cho tới khi hết khả năng xếp thêm.

Nếu có buổi thỉnh giảng không xếp được, người có quyền quản lý GV thỉnh giảng có thể
cập nhật hồ sơ/giờ có thể dạy theo thỏa thuận thực tế.

Output: TKB theo phạm vi được phép xếp; thuật toán và các ràng buộc hiện có không đổi.

### [5] Điều phối sau xếp lịch

JLE và Phòng Đào tạo điều phối nghiệp vụ sau khi có lịch. Yêu cầu hiện tại không tạo
tài khoản đăng nhập, màn hình hay quyền xếp lịch riêng cho hai đơn vị này.

Việc gán phòng cụ thể không thuộc quyền đăng nhập được xác định trong yêu cầu phân
vai này. Hiện tại ứng dụng chỉ xử lý các ràng buộc phòng theo thuật toán sẵn có.

## 4. Thông tin về Phòng học cần quản lý

Mỗi phòng cần các thông tin: tên/mã phòng, sức chứa (số SV tối đa), khu vực (Hòa
Lạc/Mỹ Đình/...), loại (Lý thuyết/Thực hành), và có thể kèm khung giờ đã bận sẵn
ngoài giảng dạy. Sau khi gán phòng ở bước [5], mỗi buổi học cần ghi rõ đã dùng đúng
phòng nào.

Với trường hợp nhiều khoa, cách tổng hợp dữ liệu phòng/TKB từ các khoa khác nhau về
một nơi chung để Phòng Đào Tạo xử lý ở bước [5] — chưa chốt, để quyết định khi triển
khai.

## 5. Nguyên tắc tính số lớp cần mở (bước [1])

Mục tiêu: **tối thiểu hoá ghế trống** (không phải tối thiểu số lớp).

- Input: tổng số SV cần học môn X trong kỳ (đã gộp SV học lại/trượt), danh sách sức
  chứa các phòng cùng loại đang có — xét chung tất cả khu vực.
- Chọn số lớp và sức chứa mục tiêu mỗi lớp sao cho tổng sức chứa các lớp đã chọn sát
  nhất với tổng số SV cần học (không được ít hơn số SV, nhưng dư ra càng ít càng tốt).
- Không cần thêm ràng buộc "sức chứa tối thiểu để mở 1 lớp" riêng: thực tế không có
  phòng nào sức chứa dưới 40 SV và không có môn nào dưới 50 SV theo học, nên mức sàn
  tự nhiên này đã tự đảm bảo không phát sinh lớp quá nhỏ bất thường.

## 6. Ràng buộc khu vực (Hòa Lạc/Mỹ Đình)

2 khu vực cách rất xa nhau, không di chuyển kịp trong ngày — ràng buộc: **trong 1
ngày, 1 giảng viên không được dạy ở cả 2 khu vực**. Ràng buộc này chỉ áp dụng cho
giảng viên; sinh viên đăng ký ở đâu học ở đó, không cần theo dõi/kiểm tra khu vực
học của SV.

Cách xử lý trong luồng:

- **Bước [4]** (GĐCT hoặc Trợ lý khoa xếp giờ) chỉ dựa vào giờ GV rảnh, không xét khu vực — vì
  phòng (và do đó khu vực) chưa được gán ở bước này.
- **Bước [5]** (Phòng Đào Tạo gán phòng) là bước duy nhất xét khu vực: vì mỗi phòng
  gắn liền đúng 1 khu vực, gán phòng tức là gán khu vực, nên ràng buộc "1 giảng viên
  không dạy 2 khu vực cùng ngày" được kiểm tra và xử lý ở đây.

Vì giờ đã chốt cứng từ [4] mà không xét khu vực, có thể (hiếm) gặp trường hợp 1 GV bị
đặt 2 buổi dạy cùng ngày mà lúc gán phòng ở [5] không tìm được cách giữ đúng 1 khu vực
cho cả ngày đó. Trường hợp này xử lý bằng cách sửa tay lại TKB giờ ở bước [4] (mục 7).

## 7. Yêu cầu cho phép sắp xếp thủ công

Ở các bước có tính toán tự động —
người phù hợp phải luôn có thể tự tay sửa/ghi đè, không bị bắt buộc dùng đúng kết quả
hệ thống tự tính ra:

| Bước tự động | Cho phép sửa tay gì |
|---|---|
| [1] Tính số lớp | Sửa tay số lớp (và/hoặc sức chứa mục tiêu mỗi lớp) trong CTĐT phụ trách |
| [4] Xếp TKB theo giờ | Tự tay xếp/sửa giờ dạy cho 1 hoặc nhiều buổi học, không bắt buộc chạy tự động |
| [5] Gán phòng | Tự tay gán/đổi phòng cụ thể cho 1 buổi học, không bắt buộc theo gán tự động |

## 8. Ngoài phạm vi tài liệu này

- Tài khoản và phân quyền bảo mật thật. Vai trò chọn trên giao diện demo không xác
  thực người dùng và không bảo vệ API.
- Người được phép nhập/nạp/chỉnh sửa dữ liệu lớp học phần và nhập file Excel: yêu
  cầu hiện tại chưa chỉ định vai trò này.
- Giao diện cụ thể cho từng vai trò.
- Cách tổng hợp dữ liệu phòng/TKB từ nhiều khoa về một nơi chung — chưa chốt.
