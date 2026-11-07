# Kiểm thử VJU-Calendar

| Thư mục / file | Nội dung |
|---|---|
| `sprint0/` | Ca chấp nhận và runner Sprint 0 |
| `sprint1/` | Ca chấp nhận và runner Sprint 1 |
| `sprint2/` | Code 10 ca TC-01…TC-10 theo báo cáo Sprint 2 và bộ S2-Bxx-yy trước đó |
| `frontend/` | Test hồi quy component, adapter, giao diện và cấu hình Vite dùng chung |
| `backend/` | Test hồi quy API, cấu hình và nghiệp vụ dùng pytest |
| `runtests.py` | Bộ kiểm thử backend tuần tự dùng chung |
| `conftest.py`, `setup.js` | Thiết lập pytest và Vitest dùng chung |

File theo Plan/Log Sprint 2 hiện tại: `sprint2/sprint2-acceptance.test.jsx`
(10 ca TC-01…TC-10, chép nguyên từ commit `36294ff`). Kết quả PASS trong Log
được tổng hợp từ báo cáo nhóm. Xem `sprint2/README.md` để phân biệt với bộ 61 ca cũ.

Chạy runner từng Sprint từ thư mục gốc project:

```powershell
& 'C:\Users\Minh\AppData\Local\Programs\Python\Python314\python.exe' -X utf8 test/sprint0/run.py
& 'C:\Users\Minh\AppData\Local\Programs\Python\Python314\python.exe' -X utf8 test/sprint1/run.py
& 'C:\Users\Minh\AppData\Local\Programs\Python\Python314\python.exe' -X utf8 test/sprint2/run.py
```

Runner Sprint 0/1 dùng bản sao để bảo vệ dữ liệu project. Runner Sprint 2 hiện
chạy 14 bài thuộc bộ S2-Bxx-yy và 4 bài hồi quy, không chạy bộ TC-01…TC-10.
Mỗi lượt chạy lưu kết quả riêng dưới `work/sprint*-tests/`.

Chạy test cấu hình Vite từ thư mục gốc:

```powershell
node --test test/frontend/test_vite_config.mjs
```

Vitest vẫn dùng `frontend/vite.config.js` và tự tìm test trong các thư mục con
của `test/`. Chỉ chạy API ghi dữ liệu trên môi trường TEST hoặc qua runner cô lập.
