# Test Sprint 1

| File | Phạm vi |
|---|---|
| `acceptance_backend.py` | S1-01 đến S1-10: nhập Excel, dữ liệu thủ công, giải hai giai đoạn và lưu toàn bộ lịch qua Flask test client. |
| `acceptance.test.jsx` | 16 bài component Sprint 1, giữ mã TC-01 đến TC-16 của bộ test hiện có. |
| `save-confirm.test.jsx` | S1-23: Hủy không lưu; Đồng ý gọi lưu một lần, không truyền bộ lọc. |
| `run.py` | Chạy các bộ trên và hồi quy REG-01, REG-02, REG-03; lưu output theo từng lượt. |

Chạy từ thư mục gốc VJU-Calendar:

```powershell
& 'C:\Users\Minh\AppData\Local\Programs\Python\Python314\python.exe' -X utf8 test/sprint1/run.py
```

Mỗi lượt tạo `work/sprint1-tests/<thời điểm>/`. API, API runner và pytest chạy trên
bản sao backend/cấu hình riêng. Frontend dùng mock API trong component tests.
Kết quả gồm JSON, JUnit XML, output và `run-summary.json` có commit/lệnh/phạm vi.

REG-03 chạy bộ hồi quy frontend thuộc phạm vi bàn giao Sprint 1 và hai bài S1-23.
Ba file `sprint2-*.test.jsx` thuộc Sprint 2 được liệt kê riêng trong summary.
S1-23 chứng minh hành vi component; chưa thay thế kiểm tra hộp xác nhận native
trên trình duyệt. Các ca UI thủ công khác vẫn đối chiếu ảnh và dữ liệu trong hồ sơ.

S1-24/QA-S1-01 vẫn mở: PO/nhóm cần xác nhận ý nghĩa AC về mốc hoàn tác. Việc tổ chức
lại mã kiểm thử không thay đổi AC hoặc tự chuyển ca này sang PASS.
