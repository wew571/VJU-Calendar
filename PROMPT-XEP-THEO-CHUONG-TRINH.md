# Prompt: thêm chức năng xếp TKB cho riêng từng chương trình (CTĐT)

> Prompt giao cho Claude Code, kèm phần ghi nhận việc đã thi công ở cuối.
> Bản này đã được **thực hiện xong và kiểm chứng trên dữ liệu thật** — giữ lại để
> rà soát, để bàn giao, và để làm khuôn cho các mở rộng tiếp theo.

---

## PHẦN 1 — PROMPT

### Bối cảnh

Dự án `FATE_VJU` là công cụ xếp thời khóa biểu cho Khoa FATE (VJU).
Backend Flask ở `webapp/`, frontend React + Vite ở `frontend/src/`.

Theo `QUY-TRINH-NGHIEP-VU-XEP-TKB.md`, một khoa có **nhiều chương trình đào tạo
(CTĐT)** — BCSE, FTH, ESAS, MJM, ECE, ESCT, BICA, BJS, "Chung" — mỗi CTĐT có một
Giám đốc Chương trình phụ trách. Mỗi lớp còn có cột **Khóa** (VJU2026, VJU2025,
VJU2024, VJU2023…).

**Vấn đề:** nút "Giải" (`/api/solve-guest`, `/api/solve-resident`) chạy CP-SAT
trên **toàn bộ** sections của khoa. Không ai xếp được phần của riêng mình: bấm
Giải là cả khoa bị xếp lại, kể cả những lớp mà chương trình khác đã thống nhất
xong giờ với giảng viên.

Bộ lọc CTĐT/Khóa hiện có ở màn Thời khóa biểu (`adapters/scheduleView.js: SCOPE`)
**chỉ là bộ lọc hiển thị**, không ảnh hưởng gì tới thuật toán.

### Yêu cầu

Thêm khái niệm **PHẠM VI XẾP** = (một CTĐT) × (một tập Khóa). Trước mắt phải dùng
được ngay cho **FTH × {VJU2026, VJU2025, VJU2024}** — 33 lớp (14 thỉnh giảng,
19 cơ hữu).

Không truyền phạm vi = toàn khoa, **hành vi cũ phải giữ nguyên từng chi tiết**.

### Bảy câu hỏi khó phải trả lời dứt khoát

1. **Giảng viên bắc cầu.** Thầy A dạy 1 lớp FTH và 1 lớp BCSE đã có giờ. Xếp FTH
   thì làm sao không đè lên giờ lớp BCSE của thầy? *(Dữ liệu thật: 10/24 giảng
   viên của phạm vi FTH còn dạy lớp ngoài phạm vi.)*
2. **Phòng dùng chung.** `ltPool=60`, `labPool=40` là tài nguyên của cả khoa.
   Xếp riêng FTH thì `AddCumulative` tính trên tập nào?
3. **Học chung bắc cầu.** Dữ liệu thật có nhóm `[#281 "Chung" – Học theo dự án
   (FTH3006), #301 FTH/VJU2023]`. Xếp phạm vi FTH thì nhóm đó xử lý ra sao?
4. **Xếp tuần tự.** Xếp FTH xong rồi xếp BCSE — kết quả FTH có bị đổi giờ không?
   Cơ chế nào giữ?
5. **Cổng chặn.** Màn "Chuẩn bị dữ liệu" đang chặn giải khi còn lớp thiếu GV/giờ
   trên **toàn khoa** (75 lớp). Xếp riêng FTH thì tính thế nào?
6. **Ô ghép.** Lớp `"FTH.ESAS"`, `"FTH+MJM"`, khóa `"VJU2024+VJU2023"` thuộc phạm
   vi nào?
7. **Chốt lịch / Hủy thay đổi / mốc hoàn tác** tương tác ra sao với phạm vi?

### Ràng buộc kỹ thuật — đọc kỹ trước khi viết dòng nào

1. **KHÔNG được cắt bớt model.** Lọc `data["sections"]` rồi giải là cái bẫy lớn
   nhất: đã đo được **2 cặp trùng giờ giảng viên** khi ghép lại với lưới của các
   CTĐT khác (`GV#88: #208↔#297`, `GV#29: #209↔#299`). Ngoài ra nếu **đại diện**
   của nhóm học chung rơi ra ngoài còn **thành viên** ở trong, thành viên chạy vào
   nhánh `continue` ở `scheduler_core.py` → mất sạch `AddNoOverlap` giảng viên và
   quota phòng, **không một dòng cảnh báo**.

2. **Đóng băng bằng THU HẸP MIỀN, không dùng interval cứng.** Đã đo: tiêm đúng 1
   xung đột vào tập đóng băng thì ghim cứng (`NewFixedSizeIntervalVar`) cho
   `INFEASIBLE`, **0/14** lớp FTH xếp được — mất trắng cả lần giải. Ghim mềm cho
   `OPTIMAL`, **14/14**, lớp xung đột được **báo tên**. File thật có dòng nhập
   trùng nên tập đóng băng không bao giờ chắc chắn sạch.

3. **Ghim mềm là chưa đủ.** Interval vẫn `Optional` nên solver có thể **hy sinh**
   một lớp của chương trình khác để xếp thêm lớp trong phạm vi — đã đo được. Phải
   có thêm một tầng trọng số trong hàm mục tiêu: mất 1 lớp ngoài phạm vi phải
   "đắt" hơn mọi tổ hợp lớp trong phạm vi cộng lại.

4. **Ô ghép tách theo THÀNH PHẦN, hai luật KHÁC NHAU.** CTĐT dùng
   `sc.section_program_names` (`PROGRAM_PART_RE`); Khóa dùng
   `tach_phan(s["cohort"], KHOA_SPLIT_RE)`. Đúng cặp hàm mà `domain/response.py`
   dùng để sinh `programParts`/`cohortParts` — dùng nhầm một luật cho cả hai là
   mất lớp khỏi bộ lọc.

5. **Bao đóng nhóm học chung là bắt buộc, và ở CẢ HAI phía.** Một thành viên vào
   phạm vi thì cả nhóm vào. Luật này phải giống hệt nhau ở `domain/pham_vi.py` và
   `adapters/phamVi.js`, nếu không màn hình đếm 15 lớp còn backend xếp 16.

6. **Chụp giờ MỘT LẦN** trước khi chạm solver. Hỏi lại giữa GD1 và GD2 sẽ ra vị
   trí do chính lần giải này vừa sinh, không phải mốc trước đó.

7. **Không xóa trắng kết quả GD2** khi có phạm vi — nghiệm của các chương trình
   khác vẫn còn nguyên giá trị.

8. **Lưu phạm vi theo TÊN, không theo `program_id`**: `get_or_create_program` cấp
   id theo thứ tự gặp và `merge.py` tính lại id khi gộp file.

9. **Danh sách CTĐT/Khóa để chọn dựng từ `data.classes`**, không từ lưới — lớp
   chưa có giờ thì chưa có buổi nào, mà đó mới đúng là lớp cần xếp nhất.

10. **`check_cross_program_conflicts` phải tiếp tục chạy trên data đầy đủ.** Nó tự
    bỏ qua giảng viên chỉ dạy 1 CTĐT, nên chạy trên tập con là nó tắt lặng lẽ đúng
    lúc rủi ro liên chương trình cao nhất.

### Quy ước code của dự án

- Chú thích **tiếng Việt, giải thích VÌ SAO** chứ không mô tả code làm gì. Backend
  viết **không dấu**, frontend viết **có dấu**.
- Chú thích nên kể được sự cố thật hoặc số đo thật đã dẫn tới quyết định đó — đọc
  `scheduler_core.py`, `domain/pinning.py` để bắt đúng giọng.
- File nhỏ theo chức năng. `domain/` không import Flask. `scheduler_core.py` không
  import gì từ `webapp`.
- Một luật chỉ được có **một** bản.

### Tiêu chí nghiệm thu

Phải đo được bằng số trên dữ liệu thật (`webapp/manual_state_snapshot.json`):

1. Xếp phạm vi FTH × {2026,2025,2024}: **0** lớp ngoài phạm vi bị xê dịch.
2. Toàn lưới: **0** cặp trùng giờ giảng viên, **0** ô giờ vượt pool phòng.
3. Xếp tuần tự cả 9 chương trình: lớp của chương trình xếp trước không bị đụng
   (trừ lớp có ô CTĐT ghép — chúng thuộc cả hai phạm vi, đây là nghiệp vụ đúng).
4. Không truyền phạm vi: kết quả **y hệt** trước khi sửa (GD1 166/166, GD2 161/161).
5. Cổng chặn tính theo phạm vi: 75 lớp toàn khoa → 10 lớp của FTH.
6. Tập đóng băng bẩn (mô phỏng file nhập trùng): **không** INFEASIBLE.

---

## PHẦN 2 — ĐÃ THI CÔNG

### Cách làm đã chốt

**Không cắt bớt model.** Toàn bộ lớp vẫn vào CP-SAT như cũ; phạm vi chỉ quyết định
**lớp nào được phép di chuyển**:

| | Lớp trong phạm vi | Lớp ngoài phạm vi |
|---|---|---|
| Có giờ trên lưới | tự do như thường lệ | **ghim cứng tại chỗ** (thu hẹp miền) + trọng số "không được hy sinh" |
| Chưa có giờ ở đâu | tự do | vẫn giữ chỗ GV/phòng, nhưng **vị trí solver bịa ra bị bỏ đi** |

Nhờ giữ nguyên tập interval, `AddNoOverlap` theo giảng viên, `AddCumulative` theo
pool phòng và ba ràng buộc nhóm học chung còn nguyên vẹn và **tự đúng** — không
phải viết bản solver thứ hai.

Ghim đi qua đúng cơ chế sẵn có của `domain/pinning.py`:
GD1 qua `submissions[sid] = [slot]`, GD2 qua tham số `ghim_tay`.

### Trả lời bảy câu hỏi

1. **GV bắc cầu** — lớp BCSE của thầy vẫn ở trong model, bị ghim tại chỗ, nên
   `AddNoOverlap` của thầy tự chặn. Đo lại: 0 cặp trùng trên toàn lưới.
2. **Phòng** — `AddCumulative` vẫn tính trên **toàn khoa** vì mọi lớp còn trong model.
3. **Học chung** — `sids_thuoc()` kéo **cả nhóm** vào phạm vi khi một thành viên
   thuộc phạm vi. Nhóm `[#281, #301]` được giữ cùng tiết 47.
4. **Xếp tuần tự** — lớp đã có giờ (kể cả giờ do lần giải trước sinh ra) đều bị
   ghim ở lần giải sau. Đo: xếp lần lượt 9 chương trình, 0 lớp bị đụng.
5. **Cổng chặn** — `guest_sections_can_thu_gio(data, chi_xet=...)` chỉ xét lớp
   trong phạm vi: 75 → **10**.
6. **Ô ghép** — thuộc **cả hai** phạm vi (phép giao khác rỗng). Nghĩa là lớp
   `FTH.ESAS` đến lượt ESAS xếp thì ESAS có quyền đổi giờ. **Cố ý không có khái
   niệm quyền sở hữu — ai xếp sau thắng**; muốn khóa cứng thì dùng "Chốt lịch theo
   học phần". Giao diện hiện số lớp dùng chung để giáo vụ biết trước.
7. **Chốt lịch giữ nguyên theo HỌC PHẦN**, không cắt theo CTĐT — đó mới là đơn vị
   cam kết thật với giảng viên. Mốc hoàn tác không đổi (vẫn một cấp, toàn cục).

### Các file

**Mới**
- `webapp/domain/pham_vi.py` — toàn bộ luật phạm vi
- `webapp/kiem_tra_pham_vi.py` — đo 3 bất biến trên dữ liệu thật
- `frontend/src/adapters/phamVi.js` — bản song sinh phía giao diện
- `frontend/src/presentation/schedule/PhamViXepPanel.jsx` — khối "Xếp cho…"

**Đã sửa** — `webapp/`: `scheduler_core.py`, `api/solve.py`, `domain/{luoi,pinning,response,__init__}.py`, `state.py`, `app.py`
· `frontend/src/`: `adapters/{buocGiai,problemInbox,scheduleView,submissionQueue,urlState}.js`, `context/AppDataContext.jsx`, `presentation/pages/SchedulePage.jsx`, `presentation/schedule/ScheduleToolbar.jsx`, `services/schedulerService.js`

### Giao diện

Khối **"Xếp cho…"** nằm ngay trên thanh tiến trình (đọc theo đúng thứ tự: *xếp cho
ai* rồi mới tới *bấm gì*): chọn 1 chương trình + tick nhiều khóa. Viền tím khi
đang có phạm vi. Ba bước của thanh tiến trình đều đếm theo phạm vi.

Thanh lọc có thêm ô **"Chỉ phạm vi đang xếp"** — độc lập với bộ lọc "Xem" sẵn có
(*tôi đang xếp cho ai* khác *tôi đang muốn nhìn gì*).

Các cảnh báo hiện ngay trên khối, không nằm im trong JSON:

| Cảnh báo | Nghĩa |
|---|---|
| `N lớp · M chưa có giờ` | quy mô phạm vi |
| `N lớp dùng chung CTĐT khác` | chương trình kia xếp lại có thể đổi giờ |
| `N lớp đã bỏ ghim nằm ngoài phạm vi — vẫn giữ chỗ` | phạm vi thắng "Bỏ ghim" |
| ⚠ `N buổi ngoài phạm vi bị đổi giờ — báo lỗi` | **lời hứa bị phá**, phải báo |
| `N buổi của CTĐT khác bị đè / mất chỗ` | giờ đang có đã xung đột sẵn |

### Đo trên dữ liệu thật (327 lớp)

```
Pham vi : FTH · VJU2026, VJU2025, VJU2024
          33 lop / 327 lop toan khoa
          47 lop ngoai pham vi CHUA co gio (chua thanh rang buoc that)

Giai doan 1 (thinh giang): OPTIMAL 1.714s   pham vi: 14/14 (vua xep moi 3)
Giai doan 2 (co huu):      OPTIMAL 0.278s   pham vi: 19/19 (vua xep moi 9)

[1] Lop ngoai pham vi bi xe dich : 0
[2] Cap trung gio giang vien     : 0
[3] O gio vuot pool phong        : 0
```

Xếp tuần tự cả 9 chương trình → 327/327 buổi, 0 trùng GV, 0 quá tải phòng.
Toàn khoa (không phạm vi) vẫn OPTIMAL 166/166 và 161/161 y như trước.

Chạy lại: `cd webapp && py kiem_tra_pham_vi.py --bo-chan FTH VJU2026 VJU2025 VJU2024`

### Giới hạn còn lại — phải biết trước khi dùng

- **47 lớp ngoài phạm vi chưa có giờ ở đâu cả** (Chung 14, BICA 10, MJM 9, BCSE 6,
  ECE 4, ESCT 3, ESAS 1). Chúng vẫn giữ chỗ GV/phòng trong model nhưng chưa phải
  ràng buộc thật — đến lượt CTĐT của chúng xếp thì chỗ tốt đã bị lấy. **Khuyên xếp
  chương trình nào nhiều lớp-chưa-giờ nhất trước.** Con số này giảm sau mỗi lần Lưu.
- **15 lớp FTH/VJU2023** (nhóm đông nhất của FTH) nằm **ngoài** phạm vi 3 khóa —
  bị đóng băng chứ không bị bỏ quên, nhưng cũng không được xếp lại.
- **Kết quả không bền qua restart Flask nếu chưa bấm "Lưu thời khóa biểu"** —
  hạn chế có sẵn của hệ thống, bản này không làm tệ hơn nhưng cũng không sửa.
- **Mốc hoàn tác vẫn một cấp, toàn cục**: xếp FTH rồi xếp BCSE là mốc "trước FTH"
  biến mất.
- **Gõ sai ô CTĐT/Khóa giờ là lỗi nặng**: một lớp gõ `VJU2O26` (chữ O) sẽ rơi khỏi
  mọi phạm vi và không bao giờ được xếp. `fate_audit` chỉ chạy ở bước xem trước
  import, chưa soi được dữ liệu đang nằm trong STATE.
- **Mục tiêu phụ "dàn đều ngày" gần như tê liệt** khi phạm vi nhỏ — cái giá không
  tránh khỏi của việc xếp lần lượt.

### Bổ sung sau: xuất Excel theo bộ lọc

Hai đường xuất, cả hai đều xuất **đúng phần đang hiện trên màn hình**:

| Đường | Nội dung | Vào từ |
|---|---|---|
| `POST /api/manual/export` | bảng "Dữ liệu học phần" khuôn FATE 29 cột, nạp lại được | Dữ liệu học phần → Xuất Excel |
| `POST /api/manual/export-luoi` | **lưới TKB** (hàng = tiết, cột = thứ), đúng bố cục màn hình | Thời khóa biểu → **Xuất lưới** |

Cách bảo đảm "khớp bộ lọc": giao diện gửi thẳng `sectionIds` đang hiện (bảng), hoặc
cả bản đồ lưới đã chia cột và tô màu (lưới) — backend **không tính lại gì**. Màn hình
mới là nơi biết chắc nó đang hiện cái gì; bắt backend đoán lại bộ lọc là mở đường cho
hai bên lệch nhau mà không ai nhìn ra.

Thuật toán chia cột được tách ra `frontend/src/adapters/luoiLayout.js` để lưới trên
màn hình và file Excel dùng **chung một bản** — chép làm hai là lần sửa sau lệch nhau.

File mới: `webapp/fate_export_luoi.py`, `frontend/src/adapters/{luoiLayout,xuatLuoi}.js`.

Cảnh báo đã cài sẵn trong hộp thoại xuất: file đã lọc nạp lại bằng chế độ "Thay thế"
sẽ **xóa các lớp không có trong file** — phải chọn "Gộp thêm".

Đo trên dữ liệu thật: lọc CTĐT=FTH → 34/313 lớp, file ra đúng 34 dòng, cột CTĐT chỉ
chứa `FTH`/`FTH+ESAS`/`FTH+MJM`/`FTH.ESAS`. Lưới: 34 buổi, đối chiếu từng ô (nội dung,
độ cao gộp, màu nền) — **0 sai lệch**.

### Bổ sung sau: bỏ qua lớp do đơn vị khác điều phối

File kế hoạch của khoa liệt kê cả những lớp khoa **không** xếp — ô giảng viên ghi
`"Phòng Đào tạo điều phối"` / `"JLE điều phối"` thay vì tên người. Đó là môn chung
(Triết học Mác-Lênin, Tư tưởng HCM, GDTC, tiếng Nhật) do đơn vị khác chịu trách nhiệm.

Dữ liệu thật: **66 lớp** (55 Phòng Đào tạo + 11 JLE), trong đó **55 là "thỉnh giảng"**
— tức chúng chiếm phần lớn danh sách đang **chặn nút Giải**.

Nút "Bỏ qua N lớp do đơn vị khác điều phối" ở màn Dữ liệu học phần đặt cờ `bo_qua`
trên section. Lớp bị bỏ qua: ẩn khỏi bảng, khỏi lưới, khỏi solver, khỏi mọi phép đếm.
**Bỏ qua chứ không xóa** — dữ liệu còn nguyên, vẫn xuất Excel được, bỏ đánh dấu là
hiện lại y nguyên.

Hai ranh giới quan trọng:

- **Không gom nhầm `"(Chưa phân công)"`** (6 lớp) — ô trống nghĩa là khoa *vẫn phải*
  tìm giảng viên rồi xếp. Chỉ bắt chữ `"điều phối"` **và** bản ghi GV là chỗ trống,
  nên `"TS. Tạ Quang Ngọc (điều phối)"` — người thật kèm ghi chú — không bị bắt oan.
- **Không chặn theo "đã chốt lịch"**. Chốt khóa cái *giờ*; bỏ qua không đụng giờ của
  lớp nào. Chặn ở đây còn làm tính năng vô dụng đúng chỗ cần nhất: 54/66 lớp này có
  giờ sẵn trong file nên đã bị auto-chốt.

Đo được: bảng 313 → 247 lớp hiện; hàng đợi "chưa sẵn sàng" **22 → 10**; cổng chặn
backend **65 → 10**; 0/66 lớp bỏ qua xuất hiện trên lưới hoặc trong "không xếp được";
bỏ đánh dấu trả về đúng nguyên trạng.

File mới: `webapp/domain/bo_qua.py`, `webapp/api/bo_qua.py`.

### Bổ sung sau: ràng buộc hai cơ sở (Hòa Lạc / Mỹ Đình)

`QUY-TRINH-NGHIEP-VU-XEP-TKB.md` mục 6: hai cơ sở cách rất xa, **trong 1 ngày 1 giảng
viên không được dạy ở cả hai**. Tài liệu nói bước [4] không xét khu vực vì phòng chưa
gán — nhưng **chính file kế hoạch đã có cột "Địa điểm giảng dạy"**: 276/313 lớp ghi
sẵn Hòa Lạc / Mỹ Đình. Đã biết thì phải dùng.

Ba việc:

1. **Địa điểm hiện trên popup chi tiết buổi** và trong file Excel xuất từ lưới.
2. **Cảnh báo "Hai cơ sở trong một ngày"** trong Hộp thư vấn đề, kèm dấu ⚠ ngay trong
   popup của từng buổi liên quan.
3. **Ràng buộc mềm trong solver** (`_rang_buoc_khu_vuc`): mỗi cặp (giảng viên, ngày)
   dính hai cơ sở là một điểm trừ. Mềm chứ không cứng — phần lớn giờ đã chốt sẵn
   trong file và có cặp vốn đã vi phạm, ràng buộc cứng sẽ làm vô nghiệm và mất trắng.

Hàm mục tiêu viết lại thành ba mức ưu tiên từ điển (`_muc_tieu`): xếp được > ít vi phạm
cơ sở > dàn đều ngày. Hệ số cũ `10*(n+1)` đủ tách mức 1 khỏi mức 3 nhưng **không đủ để
nhét mức 2 vào giữa**, nên phải tính lại.

**Chuẩn hóa bỏ dấu khi so sánh**: file thật ghi cả `"Hòa Lạc"` lẫn `"Hoà Lạc"` (đặt dấu
ở hai chữ khác nhau). Để nguyên thì thành hai khu vực và lớp `"Hoà Lạc"` duy nhất bị
báo trùng với 169 lớp còn lại. `"Online"` không tính là cơ sở — không ai phải di chuyển.

Đo được: 2 vi phạm trên dữ liệu thật (Đặng Minh Hiếu Thứ 2, Lê Viết Lan Hương Thứ 6),
**cả hai đều do giờ chốt sẵn trong file** nên solver không có quyền dịch. Thả một lớp
ra (`bỏ ghim`) thì solver tự dời Thứ 2 → Thứ 6, vi phạm 2 → 1, không buổi nào mất chỗ.
Thời gian giải không đổi (1,7s + 0,3s).

### Việc nên làm tiếp (chưa làm)

- Chạy `fate_audit` trên STATE để bắt ô CTĐT/Khóa gõ sai — giờ đã thành lỗi nặng.
- Mốc hoàn tác theo từng lần xếp phạm vi.
