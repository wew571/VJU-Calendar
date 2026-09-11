# DANH SÁCH TEST CASE TUẦN TỰ — FATE_VJU (kiểm thử qua API HTTP)

Base URL: `http://127.0.0.1:5055` (backend Flask; KHÔNG cần chạy Vite).
Chạy các test **theo đúng thứ tự TC-01 → cuối**, trong **cùng một phiên Flask**. Test sau dùng dữ liệu test trước tạo ra.

## Chuẩn bị phiên chạy (bắt buộc trước TC-01)

1. Dừng Flask nếu đang chạy.
2. Xoá `webapp/manual_state_snapshot.json` và `webapp/moc_hoan_tac.json` (để STATE khởi động hoàn toàn rỗng).
3. Khởi động lại backend: `python webapp/app.py`.
4. Hai file Excel dùng cho nhóm test import/lecturers nằm ở thư mục gốc repo:
   - `FATE.TKB.HK1 2026-2027-2.xlsx` (kế hoạch giảng dạy)
   - `List of lecturers.xlsx` (danh sách GV cơ hữu)

## Quy ước dữ liệu dùng xuyên suốt (QUAN TRỌNG — đọc trước khi chạy)

Bộ dữ liệu nhập tay mặc định của backend (`domain/sections.py: empty_manual_data`) là **7 ngày × 13 tiết/ngày** (không phải 6×6). Mọi tính toán slot trong tài liệu này theo:

```
slot = day * 13 + period      (day 0=Thứ 2 ... 5=Thứ 7, 6=Chủ nhật; period 0=tiết 1)
```

- Thứ 2 tiết 1 = slot 0; Thứ 3 tiết 1 = slot 13; Thứ 4 tiết 1 = slot 26; Thứ 5 tiết 1 = slot 39; Thứ 7 tiết 1 = slot 65; Chủ nhật tiết 1 = slot 78.
- Quy định ngày (`scheduler_core.MAX_DAY_INDEX`): GUEST (thỉnh giảng) dạy tới **Thứ 7** (day ≤ 5), RESIDENT (cơ hữu) tới **Thứ 6** (day ≤ 4). Không ai dạy Chủ nhật.
- Availability của GV GUEST chỉ chấp nhận slot < 6×13 = 78.

ID được cấp theo quy tắc "số nguyên nhỏ nhất chưa dùng" (`id_moi`), nên nếu chạy đúng tuần tự thì id sẽ đúng như tài liệu ghi. Nếu lệch, đọc id thật từ response/`GET /api/data` và thay vào các bước sau.

| Thực thể | id | Mô tả |
|---|---|---|
| GV | 0 | Nguyễn Văn A — GUEST, availability [0,1,2,13,14,15] (T2 + T3, tiết 1-3) |
| GV | 1 | Trần Thị B — RESIDENT |
| GV | 2 | Phạm Văn C — GUEST, availability lúc đầu [0], sau PATCH thành [0,1,2,3,4,5] |
| Học phần | 0 | CSE3013 "Cấu trúc dữ liệu", 3 tín chỉ |
| Học phần | 1 | CSE3014 "Cấu trúc dữ liệu (ESAS)" |
| Học phần | 2 | CSE3015 "Lập trình nâng cao" |
| Section | 0 | CSE3013-1 — GV0, 3 tiết, tự xếp, FTH/VJU2026 |
| Section | 1 | CSE3013-2 — GV1, 3 tiết, giờ chốt Thứ 4 tiết 1-3 (slot 26), FTH/VJU2026 |
| Section | 2 | CSE3014-1 — GV0, 3 tiết, tự xếp, ESAS/VJU2026 |
| Section | 3 | CSE3015-1 — GV2, 3 tiết, tự xếp, FTH/VJU2025 |
| Section | 4 | CSE3015-2 — GV2, 2 tiết, tự xếp, FTH/VJU2025 |

Trường response hay kiểm tra: `GET /api/data` trả khuôn `build_data_response` (có `classes`, `teachers`, `submissions`, `pendingSections`, `guestResult`, `residentResult`...); `GET /api/state` trả `{hasData, hasGuestResult, hasResidentResult, overridesCount}`.

---

## A. GỌI API KHI CHƯA CÓ DỮ LIỆU (STATE["data"] is None)

TC-01: Đọc trạng thái khi chưa có dữ liệu
  Mục đích: `GET /api/state` là endpoint đọc, không có `@can_du_lieu` — phải trả trạng thái rỗng chứ không lỗi.
  Tiền điều kiện: server vừa khởi động sạch (đã xoá snapshot + mốc).
  Các bước:
    1. GET /api/state
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: {"hasData": false, "hasGuestResult": false, "hasResidentResult": false, "overridesCount": 0}
    - Side-effect: không.
  Lỗi dễ gặp: endpoint bị gắn nhầm `@can_du_lieu` → trả 400, frontend màn đầu không biết trạng thái.

TC-02: GET /api/data khi chưa init
  Mục đích: decorator `@can_du_lieu` phải chặn endpoint đọc dữ liệu chính.
  Tiền điều kiện: chưa init.
  Các bước:
    1. GET /api/data
  Kết quả mong đợi:
    - HTTP status: 400
    - Body: {"error": "Chưa có dữ liệu. Hãy nạp file Excel kế hoạch giảng dạy hoặc bắt đầu nhập tay trước."}
    - Side-effect: không.

TC-03: GET /api/results khi chưa có dữ liệu — NGOẠI LỆ không 400
  Mục đích: `/api/results` là endpoint đặc biệt: chưa có data vẫn trả 200 với các giá trị null (để SPA tải lại trang không vỡ).
  Tiền điều kiện: chưa init.
  Các bước:
    1. GET /api/results
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: {"guestResult": null, "residentResult": null, "phamVi": null}
  Lỗi dễ gặp: đổi sang trả 400 → frontend F5 trắng màn.

TC-04: POST /api/manual/teacher khi chưa init
  Mục đích: endpoint ghi có `@can_du_lieu` — phải 400 trước cả khi validate body.
  Tiền điều kiện: chưa init.
  Các bước:
    1. POST /api/manual/teacher  body: {"name": "X", "teacherType": "GUEST"}
  Kết quả mong đợi:
    - HTTP status: 400
    - Body: error = "Chưa có dữ liệu..." (KHÔNG phải lỗi validate body)
  Lỗi dễ gặp: thứ tự chặn sai — validate body chạy trước → báo lỗi khác, hoặc crash vì data=None.

TC-05: POST /api/solve-guest khi chưa init
  Các bước:
    1. POST /api/solve-guest  (không body)
  Kết quả mong đợi:
    - HTTP status: 400, body error "Chưa có dữ liệu..."

TC-06: POST /api/solve-resident khi chưa init — thứ tự chặn
  Mục đích: `@can_du_lieu` phải chặn TRƯỚC kiểm tra "cần chạy Giai đoạn 1" — thông báo đúng nguyên nhân gốc.
  Các bước:
    1. POST /api/solve-resident  (không body)
  Kết quả mong đợi:
    - HTTP status: 400
    - Body: error = "Chưa có dữ liệu..." (KHÔNG phải "Cần chạy Giai đoạn 1 (thỉnh giảng) trước.")
  Lỗi dễ gặp: check guestResult chạy trước check data → người dùng nhận thông báo sai.

TC-07: POST /api/manual/course/0/chot khi chưa init
  Mục đích: `@can_du_lieu` chặn trước cả "không tìm thấy học phần".
  Các bước:
    1. POST /api/manual/course/0/chot
  Kết quả mong đợi:
    - HTTP status: 400, error "Chưa có dữ liệu..."

---

## B. KHỞI TẠO & MỐC HOÀN TÁC BAN ĐẦU

TC-08: POST /api/manual/init — khởi tạo bộ dữ liệu rỗng
  Mục đích: điểm bắt đầu luồng nhập tay; init phải XOÁ HẾT dữ liệu cũ và reset kết quả giải.
  Tiền điều kiện: bất kỳ (ở đây là chưa có dữ liệu).
  Các bước:
    1. POST /api/manual/init
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: classes rỗng (hoặc không có lớp nào), teachers rỗng; params.numDays = 7, params.slotsPerDay = 13; guestResult = null, residentResult = null
    - Side-effect: STATE["data"] = bộ rỗng; extra.sourceLabel = "Nhập liệu thủ công"; file `webapp/manual_state_snapshot.json` được ghi.
  Lỗi dễ gặp: init không gọi `reset_ket_qua()` → kết quả giải của bộ dữ liệu trước sót lại, ghim vào section id không còn nghĩa.

TC-09: GET /api/state sau init
  Các bước:
    1. GET /api/state
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: {"hasData": true, "hasGuestResult": false, "hasResidentResult": false, "overridesCount": 0}

TC-10: Hoàn tác khi chưa có mốc
  Mục đích: init KHÔNG đặt mốc hoàn tác (mốc chỉ ghi khi nạp file / lưu TKB) — hoàn tác lúc này phải báo lỗi rõ.
  Tiền điều kiện: đã init, chưa nạp file, chưa lưu TKB lần nào trong phiên.
  Các bước:
    1. POST /api/manual/hoan-tac
  Kết quả mong đợi:
    - HTTP status: 400
    - Body: error chứa "Chưa có mốc nào để quay về"
    - Side-effect: STATE không đổi.
  Lỗi dễ gặp: hoan_tac() không kiểm mốc rỗng → crash hoặc trả về trạng thái rác.

---

## C. NHẬP TAY GIẢNG VIÊN

TC-11: Thêm GV thiếu họ tên
  Các bước:
    1. POST /api/manual/teacher  body: {"teacherType": "GUEST"}
  Kết quả mong đợi:
    - HTTP status: 400, error "Thiếu Họ tên giảng viên."
    - Side-effect: teachers vẫn rỗng.

TC-12: Thêm GV với teacherType sai
  Các bước:
    1. POST /api/manual/teacher  body: {"name": "X", "teacherType": "VISITING"}
  Kết quả mong đợi:
    - HTTP status: 400, error "teacherType phải là 'GUEST' hoặc 'RESIDENT'."

TC-13: GV GUEST với availability ngoài phạm vi tuần
  Mục đích: thỉnh giảng chỉ dạy tới Thứ 7 → slot tối đa = 6×13-1 = 77; slot 78 (Chủ nhật) phải bị chặn.
  Các bước:
    1. POST /api/manual/teacher  body: {"name": "X", "teacherType": "GUEST", "availability": [78]}
  Kết quả mong đợi:
    - HTTP status: 400, error "Có slot ngoài phạm vi tuần (thỉnh giảng chỉ dạy tới Thứ 7)."
  Lỗi dễ gặp: `parse_availability_slots` quên cắt theo `max_day_index("GUEST")` → nhận cả slot Chủ nhật.

TC-14: Thêm GV GUEST hợp lệ — "Nguyễn Văn A"
  Các bước:
    1. POST /api/manual/teacher  body: {"name": "Nguyễn Văn A", "org": "FATE", "teacherType": "GUEST", "availability": [0,1,2,13,14,15]}
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: teachers có bản ghi id=0, name="Nguyễn Văn A", type="GUEST", availabilitySlots=[0,1,2,13,14,15]
    - Side-effect: data.manual_teacher_windows[0] = [0,1,2,13,14,15]; snapshot ghi lại.

TC-15: Thêm GV RESIDENT không cần availability — "Trần Thị B"
  Mục đích: cơ hữu tự do chọn giờ (GĐ2), availability bị bỏ qua — không được bắt buộc.
  Các bước:
    1. POST /api/manual/teacher  body: {"name": "Trần Thị B", "org": "FATE", "teacherType": "RESIDENT"}
  Kết quả mong đợi:
    - HTTP status: 200, teachers có id=1, type="RESIDENT"
  Lỗi dễ gặp: backend đòi availability cho cả RESIDENT.

TC-16: PATCH GV id không tồn tại
  Các bước:
    1. PATCH /api/manual/teacher/999  body: {"org": "X"}
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy giảng viên id=999"

TC-17: PATCH GV đổi tên thành rỗng
  Các bước:
    1. PATCH /api/manual/teacher/1  body: {"name": "   "}
  Kết quả mong đợi:
    - HTTP status: 400, error "Họ tên không được để trống."
    - Side-effect: tên GV1 không đổi.

TC-18: PATCH GV partial update — chỉ field có mặt mới bị ghi đè
  Mục đích: khác PATCH section (phải gửi đủ form), PATCH teacher là partial.
  Các bước:
    1. PATCH /api/manual/teacher/1  body: {"title": "ThS.", "email": "b@example.com"}
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: GV1 có title="ThS.", email="b@example.com"; name vẫn "Trần Thị B", org vẫn "FATE"
  Lỗi dễ gặp: PATCH teacher ghi đè toàn bộ bản ghi → mất name/org.

---

## D. NHẬP TAY HỌC PHẦN

TC-19: Thêm học phần thiếu tên
  Các bước:
    1. POST /api/manual/course  body: {"code": "CSE3013", "credits": 3}
  Kết quả mong đợi:
    - HTTP status: 400, error "Thiếu Tên học phần."

TC-20: Thêm học phần với credits sai kiểu
  Các bước:
    1. POST /api/manual/course  body: {"name": "X", "credits": "ba"}
  Kết quả mong đợi:
    - HTTP status: 400, error "Số tín chỉ phải là số nguyên."

TC-21: Thêm học phần CSE3013 hợp lệ
  Các bước:
    1. POST /api/manual/course  body: {"code": "CSE3013", "name": "Cấu trúc dữ liệu", "credits": 3}
  Kết quả mong đợi:
    - HTTP status: 200; courses có id=0, code="CSE3013", credits=3

TC-22: Thêm 2 học phần còn lại
  Các bước:
    1. POST /api/manual/course  body: {"code": "CSE3014", "name": "Cấu trúc dữ liệu (ESAS)", "credits": 3}
    2. POST /api/manual/course  body: {"code": "CSE3015", "name": "Lập trình nâng cao", "credits": 3}
  Kết quả mong đợi:
    - HTTP status: 200 cả hai; id lần lượt 1 và 2.

TC-23: PATCH học phần không tồn tại
  Các bước:
    1. PATCH /api/manual/course/999  body: {"name": "Y"}
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy học phần id=999"

TC-24: PATCH học phần hợp lệ
  Các bước:
    1. PATCH /api/manual/course/2  body: {"name": "Lập trình nâng cao", "credits": 2}
  Kết quả mong đợi:
    - HTTP status: 200; course 2 credits=2, code vẫn "CSE3015"

---

## E. NHẬP TAY SECTION (LỚP HỌC PHẦN)

TC-25: Thêm section thiếu giảng viên
  Các bước:
    1. POST /api/manual/section  body: {"courseId": 0, "duration": 3}
  Kết quả mong đợi:
    - HTTP status: 400, error "Lớp phải có ít nhất một giảng viên."

TC-26: Thêm section với GV không tồn tại
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [999], "courseId": 0, "duration": 3}
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy giảng viên id=999"

TC-27: Thêm section với học phần không tồn tại
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [0], "courseId": 999, "duration": 3}
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy học phần id=999"

TC-28: Thêm section với duration = 0
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [0], "courseId": 0, "duration": 0}
  Kết quả mong đợi:
    - HTTP status: 400, error "Số tiết mỗi buổi dạy phải là số nguyên > 0."

TC-29: Thêm section với khoảng tiết ngược (periodEnd < periodStart)
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [0], "courseId": 0, "duration": 3, "day": 2, "periodStart": 3, "periodEnd": 1}
  Kết quả mong đợi:
    - HTTP status: 400, error "Thứ/Tiết không hợp lệ."

TC-30: Lớp GUEST nhập giờ Chủ nhật bị chặn
  Mục đích: nhập tay phải tuân quy định ngày (thỉnh giảng tới Thứ 7) — giáo vụ gõ tay không lách được ràng buộc solver.
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [0], "courseId": 0, "duration": 3, "day": 6, "periodStart": 1, "periodEnd": 3}
  Kết quả mong đợi:
    - HTTP status: 400, error "Thỉnh giảng chỉ được dạy tới Thứ 7."

TC-31: Lớp RESIDENT nhập giờ Thứ 7 bị chặn
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [1], "courseId": 0, "duration": 3, "day": 5, "periodStart": 1, "periodEnd": 3}
  Kết quả mong đợi:
    - HTTP status: 400, error "Cơ hữu chỉ được dạy tới Thứ 6."

TC-32: Thêm section 0 — CSE3013-1 (GV0 GUEST, tự xếp)
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [0], "courseId": 0, "duration": 3, "classCode": "CSE3013-1", "program": "FTH", "cohort": "VJU2026", "autoSchedule": true}
  Kết quả mong đợi:
    - HTTP status: 200
    - Side-effect (kiểm qua GET /api/data): sections có id=0; submissions["0"] = [0, 13] (start 3 tiết duy nhất trong khung rảnh GV0: T2 tiết 1 và T3 tiết 1); lớp ở trạng thái tự xếp (time_assumed), không nằm trong pendingSections; overrides KHÔNG có key 0.
  Lỗi dễ gặp: `apply_section_time` không đọc khung rảnh GV → submissions rỗng → GĐ1 không xếp được dù GV đã khai giờ.

TC-33: Thêm section 1 — CSE3013-2 (GV1 RESIDENT, giờ đã chốt Thứ 4 tiết 1-3)
  Mục đích: giờ nhập tay = quyết định của con người → submissions rút về đúng 1 slot VÀ ghim vào overrides.
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [1], "courseId": 0, "duration": 3, "classCode": "CSE3013-2", "program": "FTH", "cohort": "VJU2026", "day": 2, "periodStart": 1, "periodEnd": 3}
    2. GET /api/state
  Kết quả mong đợi:
    - Bước 1: HTTP 200
    - Bước 2: overridesCount = 1
    - Side-effect: submissions["1"] = [26]; original_slot = 26; STATE["overrides"][1] = {"slot": 26, "reason": "Giờ đã nhập ở Dữ liệu học phần", "problem": null}
  Lỗi dễ gặp: thiếu `ghim_theo_gio_form` → lớp có giờ nhưng không ghim, lần Giải sau bị solver dời đi.

TC-34: Thêm section 2 — CSE3014-1 (GV0 GUEST, tự xếp)
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [0], "courseId": 1, "duration": 3, "classCode": "CSE3014-1", "program": "ESAS", "cohort": "VJU2026", "autoSchedule": true}
  Kết quả mong đợi:
    - HTTP status: 200; sections có id=2; submissions["2"] = [0, 13]

TC-35: Thêm GV GUEST thứ ba — "Phạm Văn C" với availability quá hẹp
  Các bước:
    1. POST /api/manual/teacher  body: {"name": "Phạm Văn C", "org": "FATE", "teacherType": "GUEST", "availability": [0]}
  Kết quả mong đợi:
    - HTTP status: 200; teachers có id=2

TC-36: Thêm section 3 — lớp thiếu giờ THẬT (đã khai nhưng không đủ dài)
  Mục đích: GV2 chỉ khai 1 slot [0] mà lớp cần 3 tiết liền → không còn khung hợp lệ → lớp vào pendingSections (xung đột thật, không được "đoán cả tuần").
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [2], "courseId": 2, "duration": 3, "classCode": "CSE3015-1", "program": "FTH", "cohort": "VJU2025", "autoSchedule": true}
  Kết quả mong đợi:
    - HTTP status: 200 (tạo lớp vẫn thành công — lỗi giờ là chuyện của bước Giải)
    - Side-effect: submissions["3"] = []; pendingSections chứa 3
  Lỗi dễ gặp: backend coi "khai rồi nhưng không đủ" như "chưa khai" → tự nới ra cả tuần, GĐ1 xếp bừa vào giờ GV không rảnh.

TC-37: Thêm section 4 — CSE3015-2 (GV2, 2 tiết, cũng thiếu giờ)
  Các bước:
    1. POST /api/manual/section  body: {"teacherIds": [2], "courseId": 2, "duration": 2, "classCode": "CSE3015-2", "program": "FTH", "cohort": "VJU2025", "autoSchedule": true}
  Kết quả mong đợi:
    - HTTP status: 200; pendingSections chứa cả 3 và 4 (2 tiết cần slot 0 và 1, GV2 mới khai mỗi slot 0)

TC-38: PATCH section thêm đồng giảng — teacherIds đủ 2 người
  Mục đích: lớp nhiều GV — khung rảnh của lớp = GIAO khung từng người.
  Các bước:
    1. PATCH /api/manual/section/2  body: {"teacherIds": [0, 2], "courseId": 1, "duration": 3, "classCode": "CSE3014-1", "program": "ESAS", "cohort": "VJU2026", "autoSchedule": true}
  Kết quả mong đợi:
    - HTTP status: 200; lớp 2 có teacherIds/teacher_ids = [0, 2]
    - Side-effect: giao khung GV0 [0,1,2,13,14,15] ∩ GV2 [0] = [0] → không đủ 3 tiết liền → submissions["2"] = [], pendingSections chứa 2
  Lỗi dễ gặp: tính khung theo GV đầu tiên thay vì giao cả nhóm → solver xếp vào giờ GV2 không rảnh.

TC-39: PATCH section bớt GV — "gửi thiếu teacherIds = mất GV" (hành vi ĐÚNG, cần ghi nhận)
  Mục đích: PATCH section là full-form; gửi teacherIds chỉ [0] thì GV2 bị gỡ khỏi lớp. Test này xác nhận hành vi để người test không báo nhầm là bug — nhưng nếu GV2 vẫn còn sau PATCH này thì MỚI là bug.
  Các bước:
    1. PATCH /api/manual/section/2  body: {"teacherIds": [0], "courseId": 1, "duration": 3, "classCode": "CSE3014-1", "program": "ESAS", "cohort": "VJU2026", "autoSchedule": true}
  Kết quả mong đợi:
    - HTTP status: 200; lớp 2 teacher_ids = [0] (GV2 mất khỏi lớp)
    - Side-effect: submissions["2"] trở lại [0, 13]; lớp 2 ra khỏi pendingSections

TC-40: PATCH section với teacherIds rỗng
  Các bước:
    1. PATCH /api/manual/section/2  body: {"teacherIds": [], "courseId": 1, "duration": 3}
  Kết quả mong đợi:
    - HTTP status: 400, error "Lớp phải có ít nhất một giảng viên."
    - Side-effect: lớp 2 không đổi (vẫn teacher_ids [0])

TC-41: Xoá section không tồn tại
  Các bước:
    1. DELETE /api/manual/section/999
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy lớp id=999"

TC-42: Bất biến dữ liệu sau khối nhập tay
  Các bước:
    1. GET /api/data
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: 3 teachers (id 0,1,2); 3 courses (id 0,1,2); 5 sections (id 0-4); pendingSections chứa [3, 4] (theo thứ tự nào đó); overrides chỉ có key "1" (slot 26)
    - guestResult = null, residentResult = null

---

## F. GIẢI LỊCH (HAI GIAI ĐOẠN)

TC-43: solve-resident khi chưa chạy Giai đoạn 1
  Mục đích: ràng buộc thứ tự bắt buộc — GĐ2 chỉ chạy sau GĐ1.
  Tiền điều kiện: có dữ liệu, guestResult = null.
  Các bước:
    1. POST /api/solve-resident  (không body)
  Kết quả mong đợi:
    - HTTP status: 400, error "Cần chạy Giai đoạn 1 (thỉnh giảng) trước."
    - Side-effect: residentResult vẫn null.

TC-44: solve-guest bị chặn khi còn lớp thỉnh giảng thiếu giờ — missingCount
  Mục đích: lớp 3, 4 của GV2 đang ở pendingSections → GĐ1 phải từ chối giải và đếm số lớp thiếu.
  Các bước:
    1. POST /api/solve-guest  (không body)
  Kết quả mong đợi:
    - HTTP status: 400
    - Body: error chứa "chưa sẵn sàng"; missingCount = 2
    - Side-effect: guestResult vẫn null.
  Lỗi dễ gặp: backend bỏ qua pendingSections → giải luôn, ra lịch không đúng điều kiện thực tế; hoặc missingCount sai (đếm cả lớp RESIDENT).

TC-45: Sửa khung giờ GV2 cho đủ dài — sync_teacher_sections tự cập nhật lớp
  Mục đích: PATCH availability phải đồng bộ lại submissions của các lớp GV đó dạy, gỡ khỏi pending.
  Các bước:
    1. PATCH /api/manual/teacher/2  body: {"availability": [0,1,2,3,4,5]}
    2. GET /api/data
  Kết quả mong đợi:
    - Bước 1: HTTP 200
    - Bước 2: pendingSections rỗng; submissions["3"] = [0,1,2,3] (start 3 tiết trong tiết 1-6); submissions["4"] = [0,1,2,3,4] (start 2 tiết)
  Lỗi dễ gặp: quên `sync_teacher_sections` → lớp vẫn nằm pending dù GV đã khai đủ giờ, GĐ1 vẫn 400.

TC-46: solve-guest thành công (toàn khoa)
  Các bước:
    1. POST /api/solve-guest  (không body)
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: lessons chứa đủ 4 lớp GUEST (id 0, 2, 3, 4); placedCount = 4; unplaced = []; phamVi = null; lessons KHÔNG chứa lớp 1 (RESIDENT — GĐ1 không biết gì về cơ hữu)
    - Ràng buộc cần kiểm thêm: lớp 0 và 2 (cùng GV0) phải ở 2 slot khác nhau và đều ∈ {0, 13}; lớp 3 và 4 (cùng GV2) không chồng tiết nhau
    - Side-effect: STATE["guestResult"] = result; STATE["pham_vi"] = null; residentResult = null (giải toàn khoa → huỷ nghiệm GĐ2 cũ); GET /api/state: hasGuestResult = true
  Lỗi dễ gặp: solver xếp 2 lớp cùng GV trùng giờ (NoOverlap hỏng); hoặc lớp 0/2 rơi vào slot ∉ {0,13} (không tôn trọng submissions).

TC-47: solve-resident thành công — lớp cơ hữu giữ giờ đã ghim
  Các bước:
    1. POST /api/solve-resident  (không body)
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: lessons chứa lớp 1 với slot = 26 (giờ đã chốt + ghim, solver không được dời); placedCount = 1; unplaced = []
    - Side-effect: STATE["residentResult"] = result; GET /api/state: hasResidentResult = true

TC-48: GET /api/results sau khi giải xong
  Các bước:
    1. GET /api/results
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: guestResult và residentResult đều khác null; guestResult.initial không phải true; phamVi = null
  Lỗi dễ gặp: endpoint trả bản cũ không gắn metadata ghim (attach_ca_hai) → thẻ buổi thiếu nhãn "đã ghim" sau F5.

TC-49: Bất biến nhóm sinh viên (MEM) — cùng (CTĐT, Khoá) không ngồi 2 lớp cùng giờ
  Mục đích: lớp 0 (guestResult) và lớp 1 (residentResult) cùng nhóm FTH/VJU2026 → không được chồng tiết.
  Các bước:
    1. GET /api/results
    2. Lấy slot + duration của lớp 0 (trong guestResult.lessons) và lớp 1 (residentResult.lessons, slot 26, 3 tiết)
    3. Kiểm tra hai khoảng [slot0, slot0+3) và [26, 29) không giao nhau
  Kết quả mong đợi:
    - Hai buổi không chồng nhau (solver đã né vì ràng buộc MEM).
  Lỗi dễ gặp: `cap_can_ne` không truyền xuống CP-SAT → sinh viên FTH/VJU2026 phải ngồi 2 lớp cùng lúc.

---

## G. KÉO-THẢ & GHIM (move-lesson / clear-override)

TC-50: move-lesson thiếu slot
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 0}
  Kết quả mong đợi:
    - HTTP status: 400, error "Thiếu hoặc sai sectionId/slot."

TC-51: move-lesson với sectionId không tồn tại
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 999, "slot": 0}
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy buổi #999"

TC-52: move-lesson slot vượt phạm vi tuần
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 0, "slot": 99999}
  Kết quả mong đợi:
    - HTTP status: 400, error "Khung giờ không hợp lệ (vượt ngày hoặc vượt tiết)."

TC-53: move-lesson lớp GUEST sang Chủ nhật
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 0, "slot": 78}
  Kết quả mong đợi:
    - HTTP status: 400, error "Thỉnh giảng chỉ được dạy tới Thứ 7."

TC-54: move-lesson lớp RESIDENT sang Thứ 7
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 1, "slot": 65}
  Kết quả mong đợi:
    - HTTP status: 400, error "Cơ hữu chỉ được dạy tới Thứ 6."
  Lỗi dễ gặp: backend check nhầm `max_day_index` theo GV chính thay vì loại lớp, hoặc không check gì.

TC-55: move-lesson thành công vào ô trống — ghi overrides + cập nhật lưới tức thì
  Mục đích: kéo-thả hợp lệ phải (a) ghi overrides[sid].slot đúng slot gửi lên, (b) PATCH ngay guestResult đang cache.
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 0, "slot": 39}
    2. GET /api/state
  Kết quả mong đợi:
    - Bước 1: HTTP 200; body {sectionId: 0, slot: 39, day: 3, period: 0, reason: null, problem: null}; guestResult.lessons của lớp 0 đã có slot = 39 ngay trong response
    - Bước 2: overridesCount = 2 (key 1 từ trước + key 0 mới)
    - Side-effect: STATE["overrides"][0] = {"slot": 39, "reason": null, "problem": null}; lớp 0 ra khỏi bo_ghim nếu có
  Lỗi dễ gặp: backend ghi overrides nhưng không cập nhật guestResult → lưới vẫn hiện ô cũ tới khi Giải lại.

TC-56: move-lesson vào ô trùng GV không ghi lý do → 409 conflict
  Mục đích: kéo-thả được phép vi phạm ràng buộc NHƯNG phải ghi lý do.
  Tiền điều kiện: lớp 0 (GV0) đang ở slot 39; lớp 2 cùng GV0.
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 2, "slot": 39}
  Kết quả mong đợi:
    - HTTP status: 409
    - Body: error chứa "cần ghi lý do"; conflict.teacherClashIds chứa 0; conflict.roomFull = false
    - Side-effect: overrides KHÔNG có key 2 (request bị từ chối, không ghi gì)
  Lỗi dễ gặp: conflict bị phát hiện nhưng override vẫn được ghi trước khi trả 409 → dữ liệu nửa vời.

TC-57: move-lesson vào ô trùng GV CÓ lý do → cho qua, lưu problem
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 2, "slot": 39, "reason": "GV xin dời, chấp nhận trùng"}
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: problem khác null (teacherClashIds chứa 0); reason khớp chuỗi gửi lên
    - Side-effect: STATE["overrides"][2] = {"slot": 39, "reason": "GV xin dời, chấp nhận trùng", "problem": {...}}; guestResult.lessons lớp 2 slot = 39

TC-58: clear-override — bỏ ghim 1 buổi (không tự lui vị trí trên lưới)
  Mục đích: bỏ ghim chỉ có hiệu lực từ lần Giải kế tiếp; buổi vẫn hiện ở chỗ cũ.
  Các bước:
    1. POST /api/clear-override  body: {"sectionId": 2}
  Kết quả mong đợi:
    - HTTP status: 200; body {sectionId: 2, cleared: true, hocChungAlso: []}
    - Side-effect: overrides mất key 2; STATE["bo_ghim"] chứa 2; guestResult.lessons lớp 2 VẪN slot 39 (không tự lui)
  Lỗi dễ gặp: chỉ xoá overrides mà không ghi bo_ghim → lần Giải sau solver vẫn ghim theo original_slot/submissions, nút "Bỏ ghim" vô dụng.

TC-59: solve-guest sau bỏ ghim — lớp được xếp lại tự do theo khung GV
  Các bước:
    1. POST /api/solve-guest  (không body)
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: lớp 2 được xếp lại vào slot ∈ {0, 13} (khung GV0) và KHÁC 39; lớp 0 vẫn ở slot 39 (override còn nguyên — ghim tay phải được tôn trọng khi giải lại)
    - Side-effect: guestResult mới; residentResult = null (toàn khoa → huỷ GĐ2 cũ)
  Lỗi dễ gặp: `tam_bo_ghim` không trả submissions về khung rảnh → lớp 2 vẫn bị ghim ở 39 dù đã bỏ ghim; hoặc override của lớp 0 bị mất sau Giải lại.

---

## H. LƯU TKB & HOÀN TÁC

TC-60: save-schedule — đóng băng lưới thành giờ chính thức của lớp
  Các bước:
    1. POST /api/manual/save-schedule  (không body)
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: savedCount = 5 (cả 5 lớp đều có slot trên lưới); problemCount = 0; missingCount = 0
    - Side-effect: mỗi section có day/period_start/period_end khớp slot đang hiện; schedule_status = "scheduled"; mốc hoàn tác được đặt (dat_moc "lần lưu thời khoá biểu"); snapshot ghi lại; guestResult/residentResult/overrides KHÔNG bị xoá
  Lỗi dễ gặp: save-schedule xoá overrides/kết quả → lưới trắng sau lưu; hoặc không ghi schedule_status.

TC-61: GET /api/state sau lưu
  Các bước:
    1. GET /api/state
  Kết quả mong đợi:
    - HTTP status: 200; hasData = true, hasGuestResult = true, hasResidentResult = false (GĐ2 bị huỷ ở TC-59, toàn khoa), overridesCount = 2 (key 0 slot 39, key 1 slot 26)

TC-62: Sửa tay sau lưu rồi hoàn tác — quay về đúng mốc lưu
  Mục đích: "Huỷ thay đổi" trả TOÀN BỘ về trạng thái lần Lưu gần nhất (giờ, ghim, lưới).
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 0, "slot": 26}   (ô này trùng nhóm SV với lớp 1 nhưng khác GV — move-lesson chỉ kiểm GV/phòng nên problem = null, cho qua)
    2. POST /api/manual/hoan-tac
    3. GET /api/results
  Kết quả mong đợi:
    - Bước 1: HTTP 200 (ghi nhận đã thay đổi: overrides[0].slot = 26)
    - Bước 2: HTTP 200; body hoanTacVe có nhan chứa "lưu thời khoá biểu", soLop = 5
    - Bước 3: guestResult.lessons lớp 0 đã quay về slot 39; overrides[0].slot = 39 (không còn 26)
  Lỗi dễ gặp: hoan_tac() gán thẳng object từ mốc thay vì deepcopy → lần sửa tiếp theo ăn vào mốc, bấm "Huỷ" lần hai ra trạng thái sai.

TC-63: Hoàn tác lần 2 — idempotent (mốc được giữ lại)
  Các bước:
    1. POST /api/manual/hoan-tac
  Kết quả mong đợi:
    - HTTP status: 200; hoanTacVe giống hệt TC-62 (cùng nhan, cùng soLop)
    - Side-effect: STATE vẫn như sau TC-62.

---

## I. HỌC CHUNG

TC-64: Tạo nhóm với ít hơn 2 lớp
  Các bước:
    1. POST /api/manual/hoc-chung  body: {"sectionIds": [0]}
  Kết quả mong đợi:
    - HTTP status: 400, error "Cần chọn ít nhất 2 lớp để đánh dấu học chung."

TC-65: Tạo nhóm với lớp không tồn tại
  Các bước:
    1. POST /api/manual/hoc-chung  body: {"sectionIds": [0, 999]}
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy lớp id=999"

TC-66: Tạo nhóm khác giai đoạn xếp lịch (GUEST + RESIDENT)
  Mục đích: hai pha giải là hai mô hình CP-SAT riêng — không thể ép cùng giờ chéo pha.
  Các bước:
    1. POST /api/manual/hoc-chung  body: {"sectionIds": [0, 1]}
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "cùng giai đoạn xếp lịch"

TC-67: Tạo nhóm khác số tiết
  Các bước:
    1. POST /api/manual/hoc-chung  body: {"sectionIds": [0, 4]}   (3 tiết vs 2 tiết)
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "cùng SỐ TIẾT"

TC-68: Tạo nhóm hợp lệ {0, 2} — đồng bộ giờ về đại diện
  Mục đích: học chung = MỘT buổi; lớp không giờ được kéo về giờ của lớp đại diện.
  Tiền điều kiện: lớp 0 đang có giờ chính thức (Thứ 5 tiết 1-3, sau TC-60/62); lớp 2 cùng GV0, 3 tiết, LT, GUEST.
  Các bước:
    1. POST /api/manual/hoc-chung  body: {"sectionIds": [0, 2], "by": "Giáo vụ", "note": "test nhóm"}
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: hocChungGroup.id = 0, sectionIds = [0, 2], classCodes = ["CSE3013-1", "CSE3014-1"]
    - Side-effect: lớp 2 được đồng bộ về giờ lớp 0 (day=3, tiết 1-3, submissions["2"] = [39]); snapshot ghi lại
  Lỗi dễ gặp: tạo nhóm nhưng không `dong_bo_gio_nhom` → hai thành viên ở hai giờ khác nhau, solver ép lại ở lần Giải sau gây nhảy lịch khó hiểu.

TC-69: GET /api/manual/hoc-chung — xem danh sách nhóm
  Các bước:
    1. GET /api/manual/hoc-chung
  Kết quả mong đợi:
    - HTTP status: 200; groups có đúng 1 nhóm, sectionIds = [0, 2]

TC-70: Tạo nhóm chồng lên nhóm đã có
  Các bước:
    1. POST /api/manual/hoc-chung  body: {"sectionIds": [0, 3]}
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "đã thuộc một nhóm học chung khác"

TC-71: Sửa section phá nhóm (đổi số tiết) → 409 hocChungLocked
  Mục đích: sửa 1 thành viên làm nhóm không còn là một buổi → từ chối, bắt tách nhóm trước.
  Các bước:
    1. PATCH /api/manual/section/0  body: {"teacherIds": [0], "courseId": 0, "duration": 2, "classCode": "CSE3013-1", "program": "FTH", "cohort": "VJU2026", "day": 3, "periodStart": 1, "periodEnd": 2}
  Kết quả mong đợi:
    - HTTP status: 409
    - Body: hocChungLocked = true; error chứa "tách nhóm học chung trước"
    - Side-effect: lớp 0 không đổi (vẫn 3 tiết)
  Lỗi dễ gặp: backend chấp nhận sửa và âm thầm tách nhóm (hoặc tệ hơn: giữ nhóm) → solver ép cùng start nhưng hai buổi dài khác nhau.

TC-72: Kéo-thả 1 thành viên = kéo cả nhóm
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 2, "slot": 13}
  Kết quả mong đợi:
    - HTTP status: 200
    - Side-effect: overrides có CẢ key 0 và key 2, cùng slot = 13; guestResult.lessons: cả lớp 0 và lớp 2 đều slot 13
  Lỗi dễ gặp: chỉ ghi override cho lớp được kéo → lần Giải sau nửa nhóm bị ghim chỗ cũ, nửa chỗ mới, nhóm vỡ.

TC-73: Xoá giờ 1 thành viên = xoá giờ cả nhóm (clear-times)
  Các bước:
    1. POST /api/manual/clear-times  body: {"sectionIds": [0]}
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: clearedCount = 2 (không phải 1); hocChungAlso chứa 2; skippedChotCount = 0
    - Side-effect: lớp 0 và 2 đều về "để hệ thống tự xếp" (time_assumed, submissions theo khung GV0); overrides mất key 0 và 2
  Lỗi dễ gặp: không mở rộng theo nhóm → lớp 2 giữ giờ cũ trong khi lớp 0 mất giờ, nhóm học chung hai nơi hai giờ.

TC-74: Xoá nhóm học chung
  Các bước:
    1. DELETE /api/manual/hoc-chung/0
  Kết quả mong đợi:
    - HTTP status: 200; body hocChungRemoved = 0
    - Side-effect: data["hoc_chung"] rỗng; hai lớp trở lại độc lập (lần Giải sau lại tính trùng GV như thường)

TC-75: Xoá nhóm không tồn tại
  Các bước:
    1. DELETE /api/manual/hoc-chung/999
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy nhóm học chung id=999"

---

## J. CHỐT LỊCH THEO HỌC PHẦN

TC-76: Chốt học phần không tồn tại
  Các bước:
    1. POST /api/manual/course/999/chot
  Kết quả mong đợi:
    - HTTP status: 400, error chứa "Không tìm thấy học phần id=999"

TC-77: Chốt học phần còn lớp chưa có giờ → 400 kèm danh sách missing
  Mục đích: chốt = cam kết giờ với GV; lớp chưa có giờ thì không có gì để cam kết.
  Tiền điều kiện: lớp 0 (thuộc course 0) vừa bị xoá giờ ở TC-73; lớp 1 có giờ 26.
  Các bước:
    1. POST /api/manual/course/0/chot  body: {"by": "Giáo vụ"}
  Kết quả mong đợi:
    - HTTP status: 400
    - Body: error chứa "chưa có giờ"; missing là mảng chứa phần tử {sectionId: 0, classCode: "CSE3013-1", ...}
    - Side-effect: course 0 chưa có trường chot.
  Lỗi dễ gặp: chốt luôn, bỏ qua lớp thiếu giờ → cam kết nửa vời với GV.

TC-78: Giải lại để lớp 0 có giờ
  Các bước:
    1. POST /api/solve-guest  (không body)
  Kết quả mong đợi:
    - HTTP status: 200; lessons chứa lớp 0 và 2 (độc lập, slot ∈ {0, 13}, khác nhau vì cùng GV0), cùng 3 và 4

TC-79: Chốt học phần thành công
  Các bước:
    1. POST /api/manual/course/0/chot  body: {"by": "Giáo vụ", "note": "đã thống nhất"}
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: chotCount = 2 (lớp 0 và 1); courseName = "Cấu trúc dữ liệu"
    - Side-effect: courses[0].chot tồn tại (by/at/soLop=2); overrides[0] và overrides[1] có reason = "Đã chốt lịch học phần"; giờ lớp 0 được ghi thành giờ chính thức (time_assumed = false)

TC-80: Kéo-thả lớp thuộc học phần đã chốt → 409 locked
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 1, "slot": 0}
  Kết quả mong đợi:
    - HTTP status: 409
    - Body: locked = true; error chứa "đã chốt lịch" và "Bỏ chốt học phần trước khi sửa giờ"
    - Side-effect: overrides[1] giữ nguyên slot 26.
  Lỗi dễ gặp: backend quên chặn lớp đã chốt ở move-lesson (chỉ ẩn nút ở frontend) → cam kết với GV bị phá âm thầm.

TC-81: PATCH section đổi giờ của lớp đã chốt → 409 locked
  Các bước:
    1. PATCH /api/manual/section/0  body: {"teacherIds": [0], "courseId": 0, "duration": 3, "classCode": "CSE3013-1", "program": "FTH", "cohort": "VJU2026", "day": 1, "periodStart": 1, "periodEnd": 3}
      (giờ khác giờ đã chốt — đọc giờ hiện tại từ GET /api/data trước để chắc chắn khác)
  Kết quả mong đợi:
    - HTTP status: 409, locked = true

TC-82: PATCH section GIỮ NGUYÊN giờ, chỉ đổi thông tin khác → cho qua
  Mục đích: khoá đúng PHẦN GIỜ, không khoá cả bản ghi — sau chốt vẫn phải sửa được ghi chú/địa điểm.
  Các bước:
    1. GET /api/data  → đọc day/periodStart/periodEnd hiện tại của lớp 0
    2. PATCH /api/manual/section/0  body: {"teacherIds": [0], "courseId": 0, "duration": 3, "classCode": "CSE3013-1", "program": "FTH", "cohort": "VJU2026", "day": <day hiện tại>, "periodStart": <ps hiện tại>, "periodEnd": <pe hiện tại>, "notes": "ghi chú mới"}
  Kết quả mong đợi:
    - HTTP status: 200; lớp 0 có notes = "ghi chú mới", giờ không đổi
  Lỗi dễ gặp: `khoa_vi_da_chot` không nhận time_info để so giờ → chặn luôn cả sửa ghi chú, học phần đã chốt thành bất khả xâm phạm.

TC-83: clear-times quét trúng lớp đã chốt — bỏ qua, đếm skippedChotCount
  Các bước:
    1. POST /api/manual/clear-times  body: {"sectionIds": [0, 1]}
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: clearedCount = 0; skippedChotCount = 2
    - Side-effect: giờ lớp 0 và 1 không đổi.
  Lỗi dễ gặp: xoá hàng loạt phá luôn giờ đã chốt.

TC-84: Bỏ chốt học phần — trả giờ về trạng thái trước chốt
  Các bước:
    1. DELETE /api/manual/course/0/chot
  Kết quả mong đợi:
    - HTTP status: 200; courseName = "Cấu trúc dữ liệu"
    - Side-effect: courses[0] mất trường chot; overrides mất key 0 và 1; lớp 1 giữ giờ 26 (trước chốt đã có giờ cố định); lớp 0 về "để hệ thống tự xếp" VÀ nằm trong bo_ghim (vì trước chốt nó chưa có giờ chính thức — giờ lấy từ solver)
  Lỗi dễ gặp: bỏ chốt nhưng không add bo_ghim cho lớp vốn chưa có giờ → giờ vừa chốt sót lại ở original_slot, solver tiếp tục ghim theo.

TC-85: Bỏ chốt học phần chưa chốt
  Các bước:
    1. DELETE /api/manual/course/0/chot
  Kết quả mong đợi:
    - HTTP status: 400, error "Học phần này chưa được chốt."

---

## K. BỎ QUA (LỚP DO ĐƠN VỊ KHÁC ĐIỀU PHỐI)

TC-86: Xem ứng viên bỏ qua — dữ liệu nhập tay không có ứng viên
  Mục đích: ứng viên = lớp có GV PLACEHOLDER ghi "điều phối" (chỉ sinh ra từ file Excel); dữ liệu nhập tay không có → danh sách rỗng, nhưng endpoint vẫn phải trả đủ cấu trúc.
  Các bước:
    1. GET /api/manual/bo-qua
  Kết quả mong đợi:
    - HTTP status: 200; body {"ungVien": [], "soUngVien": 0, "dangBoQua": []}

TC-87: Đánh dấu bỏ qua với sectionIds sai kiểu
  Các bước:
    1. POST /api/manual/bo-qua  body: {"sectionIds": "abc", "boQua": true}
  Kết quả mong đợi:
    - HTTP status: 400, error "sectionIds phải là danh sách."

TC-88: Đánh dấu bỏ qua thủ công lớp 3
  Các bước:
    1. POST /api/manual/bo-qua  body: {"sectionIds": [3], "boQua": true}
  Kết quả mong đợi:
    - HTTP status: 200; boQuaChanged = [3]; boQua = true; soDangBoQua = 1
    - Side-effect: sections[3].bo_qua = true; snapshot ghi lại.
  Lỗi dễ gặp: endpoint chặn theo "đã chốt lịch" — SAI nghiệp vụ (bỏ qua không động vào giờ, không liên quan cam kết chốt).

TC-89: Kéo-thả lớp bị bỏ qua → 409 (không phải 409 locked)
  Mục đích: khoa không được đổi giờ lớp do đơn vị khác điều phối; thông báo phải đúng nguyên nhân (khác với "đã chốt lịch").
  Các bước:
    1. POST /api/move-lesson  body: {"sectionId": 3, "slot": 0}
  Kết quả mong đợi:
    - HTTP status: 409
    - Body: error chứa "do đơn vị khác điều phối"; KHÔNG có trường locked (để frontend phân biệt với chốt lịch)
  Lỗi dễ gặp: thứ tự chặn sai — nếu lớp bỏ qua mà thuộc học phần đã chốt, phải báo "đơn vị khác điều phối" TRƯỚC, không thì người dùng bỏ chốt xong vẫn bị từ chối.

TC-90: Giải lại GĐ1 — lớp bỏ qua không vào solver
  Các bước:
    1. POST /api/solve-guest  (không body)
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: lessons KHÔNG chứa lớp 3 (ngoài bài toán); lớp 0, 2, 4 được xếp bình thường
  Lỗi dễ gặp: lớp bỏ qua vẫn vào model → chiếm phòng/GV và bị solver gán giờ bừa.

TC-91: Bỏ đánh dấu bỏ qua lớp 3
  Các bước:
    1. POST /api/manual/bo-qua  body: {"sectionIds": [3], "boQua": false}
  Kết quả mong đợi:
    - HTTP status: 200; boQuaChanged = [3]; soDangBoQua = 0
    - Side-effect: sections[3].bo_qua = false; lớp 3 lại là việc của khoa.

---

## L. PHẠM VI XẾP (THEO CTĐT + KHOÁ)

TC-92: solve-guest với phamVi FTH/VJU2025 — lớp ngoài phạm vi bị đóng băng
  Mục đích: xếp riêng 1 CTĐT + khoá KHÔNG được xê dịch lớp của chương trình khác.
  Tiền điều kiện: ghi lại slot hiện tại của lớp 0, 1, 2 (GET /api/results) trước khi chạy.
  Các bước:
    1. GET /api/results  (chụp slot lớp 0, 1, 2)
    2. POST /api/solve-guest  body: {"phamVi": {"programs": ["FTH"], "cohorts": ["VJU2025"]}}
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: phamVi khác null; phamVi.moTa chứa "FTH" và "VJU2025"; phamVi.tong = 2 (lớp 3 và 4 — GUEST trong phạm vi); phamVi.ngoaiPhamViBiDoiGio = 0 (CHỐT TỰ KIỂM CHỨNG — khác 0 là có bug)
    - lessons của lớp 0 và 2 (ngoài phạm vi, đang có giờ) giữ NGUYÊN slot đã chụp ở bước 1
    - Side-effect: STATE["pham_vi"] = {"programs": ["FTH"], "cohorts": ["VJU2025"]}
  Lỗi dễ gặp: ghim ngoài phạm vi (`ghim_ngoai_pham_vi`) không trả submissions lại sau giải, hoặc solver hy sinh lớp ngoài phạm vi (`uu_tien_giu` thiếu) → lịch chương trình khác bị xáo.

TC-93: solve-resident giữ đúng phạm vi của GĐ1 (body rỗng)
  Mục đích: GĐ2 phải chạy ĐÚNG phạm vi GĐ1 đã đóng băng — frontend chỉ POST không body, backend phải tự giữ.
  Các bước:
    1. POST /api/solve-resident  (không body)
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: lớp 1 (FTH/VJU2026 — NGOÀI phạm vi) giữ slot 26; phamVi.tong = 0 (không lớp RESIDENT nào thuộc FTH/VJU2025)
    - Side-effect: residentResult mới; STATE["pham_vi"] vẫn FTH/VJU2025.
  Lỗi dễ gặp: body rỗng bị hiểu là "toàn khoa" → GĐ2 xếp lại lớp của chương trình khác, phá đúng thứ tính năng này sinh ra để bảo vệ.

TC-94: phamVi rỗng cả hai vế → quay về toàn khoa
  Mục đích: {"programs": [], "cohorts": []} phải là toàn khoa, KHÔNG phải "không lớp nào".
  Các bước:
    1. POST /api/solve-guest  body: {"phamVi": {"programs": [], "cohorts": []}}
  Kết quả mong đợi:
    - HTTP status: 200; phamVi = null; lessons chứa đủ các lớp GUEST (0, 2, 3, 4)
    - Side-effect: STATE["pham_vi"] = null; residentResult bị reset (giải toàn khoa → nghiệm GĐ2 cũ hết hiệu lực)
  Lỗi dễ gặp: `chuan_hoa` trả phạm vi rỗng thay vì None → bấm Giải ra 0 lớp không hiểu vì sao.

TC-95: phamVi sai kiểu (không phải object) → coi như toàn khoa
  Các bước:
    1. POST /api/solve-guest  body: {"phamVi": "FTH"}
  Kết quả mong đợi:
    - HTTP status: 200; phamVi = null (hành vi hiện tại: chuẩn hoá trả None, không 400)
  Ghi chú: đây là hành vi "tha thứ" có chủ đích của backend; nếu muốn chặt (400) thì là thay đổi thiết kế, không phải bug.

---

## M. XOÁ SECTION & DỌN MÃ LỚP

TC-96: Xoá section 0 — các lớp cùng học phần đồn số lên
  Mục đích: xoá "CSE3013-1" thì "CSE3013-2" phải thành "CSE3013-1" (không để trống số giữa); đồng thời dọn submissions/overrides tham chiếu treo.
  Tiền điều kiện: course 0 đã bỏ chốt (TC-84); nhóm học chung đã xoá (TC-74).
  Các bước:
    1. DELETE /api/manual/section/0
    2. GET /api/data
  Kết quả mong đợi:
    - Bước 1: HTTP 200
    - Bước 2: không còn section id 0; lớp id 1 có classCode = "CSE3013-1" (đồn từ -2); submissions/overrides không còn key 0; guestResult.lessons không còn buổi "ma" của lớp 0 (đã dong_bo_ket_qua)
  Lỗi dễ gặp: xoá lớp nhưng không dọn guestResult/residentResult cache → lớp đã xoá vẫn hiện "ma" trên lưới tới khi Giải lại.

TC-97: Bất biến sau xoá
  Các bước:
    1. GET /api/state
  Kết quả mong đợi:
    - HTTP status: 200; overridesCount chỉ còn đếm các ghim hợp lệ (không còn key 0); hasData = true

---

## N. XUẤT EXCEL

TC-98: export GET — xuất toàn bộ bảng dữ liệu học phần
  Các bước:
    1. GET /api/manual/export
  Kết quả mong đợi:
    - HTTP status: 200
    - Header: Content-Type = application/vnd.openxmlformats-officedocument.spreadsheetml.sheet; Content-Disposition có filename dạng "FATE.TKB.TKB.xlsx"
    - Body là file .xlsx hợp lệ (mở bằng openpyxl được)

TC-99: export POST với sectionIds sai kiểu
  Các bước:
    1. POST /api/manual/export  body: {"sectionIds": "abc"}
  Kết quả mong đợi:
    - HTTP status: 400, error "sectionIds phải là danh sách."

TC-100: export POST với bộ lọc rỗng
  Mục đích: frontend lọc ra 0 lớp thì không được xuất file rỗng.
  Các bước:
    1. POST /api/manual/export  body: {"label": "test", "sectionIds": []}
  Kết quả mong đợi:
    - HTTP status: 400, error "Bộ lọc hiện tại không còn lớp nào để xuất."

TC-101: export POST có lọc — chỉ đúng các lớp đang hiện
  Các bước:
    1. POST /api/manual/export  body: {"label": "FTH-VJU2025", "sectionIds": [3, 4]}
    2. Mở file tải về bằng openpyxl, đếm dòng dữ liệu
  Kết quả mong đợi:
    - HTTP status: 200; filename "FATE.TKB.FTH-VJU2025.xlsx"
    - File chỉ chứa 2 lớp (CSE3015-1, CSE3015-2), đúng thứ tự sectionIds gửi lên
  Lỗi dễ gặp: backend bỏ qua sectionIds và xuất hết → file gửi đi lẫn lớp của chương trình khác.

TC-102: export-luoi thiếu cells
  Các bước:
    1. POST /api/manual/export-luoi  body: {"label": "t"}
  Kết quả mong đợi:
    - HTTP status: 400, error "Thiếu dữ liệu lưới để xuất."

TC-103: export-luoi cells rỗng
  Các bước:
    1. POST /api/manual/export-luoi  body: {"label": "t", "cells": []}
  Kết quả mong đợi:
    - HTTP status: 400, error "Bộ lọc hiện tại không còn buổi nào để xuất."

TC-104: export-luoi hợp lệ
  Các bước:
    1. POST /api/manual/export-luoi  body:
       {"label": "test", "slotsPerDay": 13,
        "tenNgay": ["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ nhật"],
        "soCotMoiNgay": [1,1,1,1,1,1,1],
        "cells": [{"day": 0, "period": 0, "duration": 3, "col": 0,
                   "maLop": "CSE3013-1", "tenMon": "Cấu trúc dữ liệu",
                   "giangVien": "Nguyễn Văn A", "soTiet": 3, "loaiPhong": "LT",
                   "mau": {"bg": "#ccfbf1", "text": "#0f766e", "border": "#5eead4"}}]}
  Kết quả mong đợi:
    - HTTP status: 200; filename dạng "FATE.TKB.test.luoi.xlsx"; mở được bằng openpyxl, ô đầu tiên chứa "CSE3013-1"

---

## O. NẠP FILE EXCEL (import preview/commit/issues)

Lưu ý nhóm này: multipart form-data, tên field file là `file`. Ví dụ:
`curl -X POST -F "file=@FATE.TKB.HK1 2026-2027-2.xlsx" http://127.0.0.1:5055/api/manual/import/preview`

TC-105: commit khi chưa preview
  Các bước:
    1. POST /api/manual/import/commit  body: {"mode": "replace"}
  Kết quả mong đợi:
    - HTTP status: 400, error "Chưa có bản xem trước. Hãy tải file lên trước."

TC-106: preview không đính kèm file
  Các bước:
    1. POST /api/manual/import/preview  (multipart rỗng)
  Kết quả mong đợi:
    - HTTP status: 400, error "Chưa chọn file."

TC-107: issues.xlsx khi chưa preview
  Các bước:
    1. GET /api/manual/import/issues.xlsx
  Kết quả mong đợi:
    - HTTP status: 400, error "Chưa có bản xem trước. Hãy tải file lên trước."

TC-108: preview file thật — KHÔNG ghi gì vào STATE
  Mục đích: preview chỉ đọc; dữ liệu nhập tay hiện tại phải còn nguyên.
  Các bước:
    1. POST /api/manual/import/preview  (multipart, file = FATE.TKB.HK1 2026-2027-2.xlsx)
    2. GET /api/data
  Kết quả mong đợi:
    - Bước 1: HTTP 200; body có summary.soLopDungDuoc > 0, summary.soGiangVien > 0, fileName đúng; có các nhóm skippedGroups/warningGroups/dataIssues
    - Bước 2: vẫn thấy các lớp nhập tay (CSE3015-1...) — STATE chưa bị động vào
  Lỗi dễ gặp: preview ghi thẳng STATE → người dùng "xem thử" mà mất dữ liệu đang làm.

TC-109: issues.xlsx sau preview
  Các bước:
    1. GET /api/manual/import/issues.xlsx
  Kết quả mong đợi:
    - HTTP status: 200; filename dạng "Loi-du-lieu.FATE.TKB.HK1 2026-2027-2.xlsx"; file xlsx hợp lệ
    - Side-effect: không (doc-only).

TC-110: commit với mode sai
  Các bước:
    1. POST /api/manual/import/commit  body: {"mode": "append"}
  Kết quả mong đợi:
    - HTTP status: 400, error "mode phải là 'replace' hoặc 'merge'."
    - Side-effect: STATE không đổi; import_pending vẫn còn (commit sau vẫn dùng được).

TC-111: commit mode "merge" — gộp thêm, dữ liệu cũ còn nguyên
  Các bước:
    1. POST /api/manual/import/commit  body: {"mode": "merge"}
    2. GET /api/data
  Kết quả mong đợi:
    - Bước 1: HTTP 200; mergeReport.soLopThem > 0; mergeReport.soLopTrung = 0 (file chưa từng nạp); có mergeReport.soGvThem, soHocPhanThem; extra.importedFrom chứa "FATE.TKB.HK1 2026-2027-2.xlsx"
    - Bước 2: các lớp nhập tay (id 1-4, CSE3015...) vẫn còn — merge KHÔNG xoá dữ liệu cũ
    - Side-effect: guestResult/residentResult được đặt lại thành LỊCH BAN ĐẦU từ giờ trong file (initial = true); mốc hoàn tác "lúc vừa nạp ..." được ghi
  Lỗi dễ gặp: merge ghi đè mất dữ liệu nhập tay; hoặc không reset kết quả giải cũ → lưới hiện buổi của section id không còn nghĩa.

TC-112: solve-resident ngay sau import — chặn vì guestResult chỉ là lịch ban đầu (initial)
  Mục đích: ràng buộc "GĐ2 yêu cầu GĐ1 đã chạy THẬT" — guestResult.initial = true không tính.
  Các bước:
    1. POST /api/solve-resident  (không body)
  Kết quả mong đợi:
    - HTTP status: 400, error "Cần chạy Giai đoạn 1 (thỉnh giảng) trước."
  Lỗi dễ gặp: chỉ kiểm `guestResult is None` mà không kiểm `initial` → GĐ2 chạy trên lịch chưa qua GĐ1.

TC-113: nạp LẠI cùng một file ở mode merge — không nhân đôi lớp
  Mục đích: gộp theo khoá lớp (mã lớp + học phần + GV + giờ); nạp lại đúng file cũ phải nhận ra trùng.
  Các bước:
    1. POST /api/manual/import/preview  (cùng file FATE.TKB.HK1 2026-2027-2.xlsx)
    2. POST /api/manual/import/commit  body: {"mode": "merge"}
  Kết quả mong đợi:
    - HTTP status: 200; mergeReport.soLopThem = 0; mergeReport.soLopTrung > 0 (≈ số lớp của file)
    - Side-effect: số lớp trong GET /api/data không đổi so với sau TC-111.
  Lỗi dễ gặp: khoá trùng (`sections.khoa_lop`) tính sai → nạp lại file nhân đôi toàn bộ lớp.

TC-114: commit mode "replace" — xoá hết, thay bằng dữ liệu file
  Các bước:
    1. POST /api/manual/import/preview  (cùng file)
    2. POST /api/manual/import/commit  body: {"mode": "replace"}
    3. GET /api/data
  Kết quả mong đợi:
    - Bước 2: HTTP 200; KHÔNG có mergeReport (replace không gộp); extra.importedFrom chỉ chứa tên file (không còn dấu " + " của merge)
    - Bước 3: các lớp nhập tay (CSE3013-1, CSE3015...) đã biến mất; chỉ còn lớp từ file
    - Side-effect: overrides/bo_ghim/pham_vi của bộ cũ bị reset; mốc hoàn tác mới "lúc vừa nạp ..."
  Lỗi dễ gặp: replace không gọi reset kết quả/ghim → ghim cũ trỏ vào section id của bộ mới (ghim bậy).

TC-115: commit 2 lần liên tiếp — lần 2 phải 400 (pending đã bị tiêu thụ)
  Các bước:
    1. POST /api/manual/import/commit  body: {"mode": "replace"}   (không preview lại)
  Kết quả mong đợi:
    - HTTP status: 400, error "Chưa có bản xem trước. Hãy tải file lên trước."
  Lỗi dễ gặp: import_pending không được dọn sau commit → commit kép ghi hai lần.

---

## P. DANH SÁCH GV CƠ HỮU (lecturers preview/commit/clear)

TC-116: lecturers/commit khi chưa preview
  Các bước:
    1. POST /api/manual/lecturers/commit
  Kết quả mong đợi:
    - HTTP status: 400, error "Chưa có bản xem trước. Hãy tải file lên trước."

TC-117: lecturers/preview không file
  Các bước:
    1. POST /api/manual/lecturers/preview  (multipart rỗng)
  Kết quả mong đợi:
    - HTTP status: 400, error "Chưa chọn file."

TC-118: lecturers/preview file thật — đối chiếu với GV đang có
  Các bước:
    1. POST /api/manual/lecturers/preview  (multipart, file = List of lecturers.xlsx)
  Kết quả mong đợi:
    - HTTP status: 200
    - Body: count > 0; có đủ các trường đối chiếu: soGvDangCo, khop, doiSangCoHuu (mảng), doiSangThinhGiang (mảng), khongDay (mảng); sample là danh sách tên
    - Side-effect: chỉ ghi STATE["co_huu_pending"]; STATE["co_huu"] chưa đổi (GET /api/manual/lecturers vẫn loaded = false)
  Lỗi dễ gặp: preview áp luôn vào STATE → "xem trước ai bị đổi loại" mất ý nghĩa.

TC-119: lecturers/commit — phân loại lại toàn bộ GV
  Các bước:
    1. POST /api/manual/lecturers/commit
    2. GET /api/manual/lecturers
  Kết quả mong đợi:
    - Bước 1: HTTP 200; count khớp preview; changed là mảng (mỗi phần tử {id, name, tu, sang}) — với file HK1 thật thường có GV bị đổi loại so với luật cũ theo ô đơn vị; hocChungSplit là mảng (có thể rỗng)
    - Bước 2: loaded = true; count khớp; fileName đúng
    - Side-effect: STATE["co_huu"] được đặt; co_huu_pending = null; các lớp của GV bị đổi loại chuyển giai đoạn xếp lịch tương ứng
  Lỗi dễ gặp: commit đổi type GV nhưng không `sync_teacher_sections` → lớp của GV vừa đổi loại kẹt ở giai đoạn cũ.

TC-120: lecturers/clear — quay về luật cũ theo ô đơn vị
  Các bước:
    1. DELETE /api/manual/lecturers
    2. GET /api/manual/lecturers
  Kết quả mong đợi:
    - Bước 1: HTTP 200; loaded = false; changed là mảng (GV đổi ngược lại)
    - Bước 2: loaded = false, count = 0

---

## Q. DỌN DẸP CUỐI PHIÊN (để chạy lại từ đầu)

TC-121: init lại — xoá sạch dữ liệu file vừa nạp
  Các bước:
    1. POST /api/manual/init
    2. GET /api/state
    3. GET /api/data
  Kết quả mong đợi:
    - Bước 1: HTTP 200
    - Bước 2: {"hasData": true, "hasGuestResult": false, "hasResidentResult": false, "overridesCount": 0}
    - Bước 3: classes rỗng, teachers rỗng — không còn sót lớp nào từ file Excel
  Lỗi dễ gặp: init không reset pham_vi/overrides → phiên chạy lại bị dính trạng thái phiên trước.

TC-122: (Thăm dò hành vi — KHÔNG phải pass/fail cứng) hoàn tác sau init
  Mục đích: ghi nhận hành vi hiện tại: init KHÔNG xoá mốc hoàn tác — mốc "lúc vừa nạp file" (TC-111/114) vẫn còn, nên hoàn tác lúc này sẽ kéo lại TOÀN BỘ dữ liệu file vừa bị init xoá. Đây là điểm cần team quyết định: có nên xoá mốc khi init không?
  Các bước:
    1. POST /api/manual/hoan-tac
  Kết quả mong đợi (hành vi hiện tại):
    - HTTP status: 200; hoanTacVe.nhan chứa "lúc vừa nạp"; GET /api/data lại thấy dữ liệu file Excel
  Ghi chú: nếu team coi đây là bug, kỳ vọng đúng là 400 "Chưa có mốc nào để quay về" — ghi nhận kết quả thực tế vào báo cáo.

TC-123: init lần cuối — kết thúc phiên ở trạng thái sạch
  Các bước:
    1. POST /api/manual/init
    2. GET /api/state
  Kết quả mong đợi:
    - HTTP 200; hasData = true, các cờ còn lại false, overridesCount = 0
    - Phiên kết thúc sạch; muốn chạy lại toàn bộ: xoá 2 file snapshot/mốc, restart Flask, quay lại TC-01.

---

## PHỤ LỤC A — Test thủ công ngoài luồng tuần tự (cần restart server)

PA-1: Persistence qua restart (snapshot)
  1. Ở một trạng thái bất kỳ có dữ liệu (vd sau TC-79), kiểm tra file `webapp/manual_state_snapshot.json` tồn tại và chứa sections.
  2. Dừng Flask, khởi động lại `python webapp/app.py`.
  3. GET /api/data → dữ liệu y hệt trước restart (teachers/courses/sections/overrides).
  4. GET /api/state → hasGuestResult/hasResidentResult = false (kết quả giải KHÔNG persist — phải bấm Giải lại). Đây là hành vi ĐÚNG theo thiết kế.

PA-2: Persistence mốc hoàn tác qua restart
  1. Sau khi đã có mốc (save-schedule hoặc import), restart Flask.
  2. POST /api/manual/hoan-tac → 200 (mốc nạp lại từ `webapp/moc_hoan_tac.json`), không phải 400 "Chưa có mốc".

## PHỤ LỤC B — Bảng tra nhanh mã lỗi theo ràng buộc

| Ràng buộc | Endpoint | Status | Trường nhận diện |
|---|---|---|---|
| Chưa có dữ liệu (`@can_du_lieu`) | mọi endpoint sửa/đọc data | 400 | error = "Chưa có dữ liệu..." |
| GĐ2 trước GĐ1 (kể cả guestResult.initial) | POST /api/solve-resident | 400 | error = "Cần chạy Giai đoạn 1..." |
| Lớp thỉnh giảng thiếu GV/giờ | POST /api/solve-guest | 400 | missingCount |
| Kéo-thả lớp đã chốt | POST /api/move-lesson | 409 | locked = true |
| Kéo-thả lớp đơn vị khác điều phối | POST /api/move-lesson | 409 | error chứa "đơn vị khác điều phối" (KHÔNG có locked) |
| Kéo-thả trùng GV/hết phòng thiếu lý do | POST /api/move-lesson | 409 | conflict = {teacherClashIds, roomFull, ...} |
| Kéo quá ngày quy định | POST /api/move-lesson | 400 | error "chỉ được dạy tới ..." |
| Sửa section phá nhóm học chung | PATCH /api/manual/section/<id> | 409 | hocChungLocked = true |
| clear-times trúng lớp chốt | POST /api/manual/clear-times | 200 | skippedChotCount > 0 |
| Chốt học phần còn lớp thiếu giờ | POST .../chot | 400 | missing = [...] |
| Bỏ chốt học phần chưa chốt | DELETE .../chot | 400 | error "chưa được chốt" |
| Export bộ lọc rỗng | POST /api/manual/export | 400 | error "không còn lớp nào" |
| Export-luoi thiếu/rỗng cells | POST /api/manual/export-luoi | 400 | error tương ứng |
| Commit khi chưa preview | import/commit, lecturers/commit | 400 | error "Chưa có bản xem trước" |
| Mode import sai | POST /api/manual/import/commit | 400 | error "mode phải là..." |
| Hoàn tác chưa có mốc | POST /api/manual/hoan-tac | 400 | error "Chưa có mốc nào..." |
