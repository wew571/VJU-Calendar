# Test Sprint 0

Đây là vị trí mã nguồn để chạy lại các kiểm tra dùng cho Test Log Sprint 0.

| File | Nội dung |
|---|---|
| `acceptance_backend.py` | Các kiểm tra API TC-08, TC-11, TC-12, TC-14, TC-15 và TC-17; quan sát ký tự đặc biệt cho TC-13. |
| `browser-checks.mjs` | Giao diện, popup, quy trình xếp lịch và xác nhận khai giờ hàng loạt trong Chrome. |
| `flask_bridge.py` | Chuyển yêu cầu của trình duyệt tới Flask test client trong bản sao kiểm thử. |
| `run.py` | Tạo bản sao mới, chạy API, build giao diện và chạy kiểm tra trình duyệt. |

Chạy từ thư mục gốc VJU-Calendar:

```powershell
& 'C:\Users\Minh\AppData\Local\Programs\Python\Python314\python.exe' -X utf8 test/sprint0/run.py
```

Chỉ chạy API:

```powershell
& 'C:\Users\Minh\AppData\Local\Programs\Python\Python314\python.exe' -X utf8 test/sprint0/run.py --api-only
```

Mỗi lần chạy tạo thư mục riêng tại `work/sprint0-tests/<thời điểm>/`, gồm bản sao,
kết quả JSON, output và ảnh. Script không chạy trên dữ liệu nghiệp vụ thật và không
ghi đè minh chứng đã nộp. Các bản chụp nguồn trong hồ sơ `Sprint 0/Minh_chung` vẫn
được giữ để đối chiếu lần chạy đã ghi trong Test Log.

Python cần các thư viện backend của dự án. Frontend cần `node_modules` đã cài.
Playwright được tìm trong dependency frontend trước, rồi dùng runtime Codex hiện
có trên máy. Chrome mặc định ở `C:/Program Files/Google/Chrome/Application/chrome.exe`;
có thể chọn executable khác bằng `VJU_TEST_CHROME`.

Exit code 1 nghĩa là có kiểm tra FAIL. Bản hiện tại còn TC-02 không đạt yêu cầu
viền đỏ ở trạng thái thường. API/Chrome chạy được không có nghĩa mọi ca trong
Test Plan đã PASS: ca tài liệu, cơ chế Tester và khuôn mẫu chờ PO vẫn theo giới hạn
ghi trong Test Log.
