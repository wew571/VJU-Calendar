# Kiểm thử Sprint 2

`sprint2-acceptance.test.jsx` chứa 10 ca TC-01 đến TC-10 tương ứng Plan/Log
đã tổng hợp theo báo cáo nhóm ngày 05/11/2026. File được chép nguyên từ commit
`36294ff`, chưa chạy lại trên bản Sprint 2. Kết quả 10/10 PASS trong Log là
kết quả do báo cáo nhóm công bố.

Các mã S2-Bxx-yy dưới đây thuộc Test Plan cũ gồm 61 ca, lập ngày 04/11/2026.
Bản Plan/Log cũ được giữ trong `Sprint 2/Minh_chung/2026-11-05-before-report-alignment/`
của thư mục tài liệu nhóm. `run.py` vẫn chạy bộ 14 bài S2-Bxx-yy và 4 bài hồi quy,
không chạy file 10 ca TC-01 đến TC-10.
Mỗi bài test đặt mã ca ngay đầu tên để đối chiếu với kết quả Vitest.

| File | Ca có mã kiểm thử |
|---|---|
| sprint2-search.test.jsx | S2-B01-01 đến S2-B01-06 |
| sprint2-navigation.test.jsx | S2-B02-01, 02, 03, 04, 06 |
| sprint2-guide.test.jsx | S2-B03-01 đến S2-B03-03, phần nội dung hướng dẫn trong ứng dụng |

Chạy từ thư mục gốc VJU-Calendar:

```powershell
& 'C:\Users\Minh\AppData\Local\Programs\Python\Python314\python.exe' -X utf8 test/sprint2/run.py
```

Đây là kiểm thử component và App shell qua jsdom. Search dùng trang tìm kiếm thật,
mock dữ liệu đầu vào, phần hiển thị bảng và các form không liên quan. Navigation
dùng App, URL adapter, layout và sidebar thật, mock providers và nội dung trang con.
Không gọi API thật hoặc sửa dữ liệu nghiệp vụ.

S2-B02-02 còn cần F5 thật và bộ lọc trang con Giảng viên. S2-B02-03 kiểm tra lịch sử
qua Dữ liệu học phần / Thời khóa biểu / Hướng dẫn và còn cần chạy đúng chuỗi tới
trang con Giảng viên. S2-B02-04 chưa kiểm tra bộ lọc URL sai hoặc chính sách fallback
đã thống nhất. Ba ca BL03 mới kiểm nội dung trong app, còn cần đối chiếu repo và
quan sát lưu/hoàn tác/xuất trên bản sao. Không dùng các kết quả này để kết luận
API phân quyền, dữ liệu CSDL hoặc toàn bộ AC đạt.

47 ca chưa có mã tự động cần phần bàn giao CSDL, xác thực, quyền, phiên bản,
migration, backup, vận hành hoặc kiểm tra hồ sơ. Không tạo test skip hoặc mock
API chưa tồn tại để tính là đã phủ.

`cases.json` ánh xạ đủ 61 mã ca với Test Plan, mức độ tự động và phần còn thiếu.
Mỗi lần chạy tạo thư mục mới `work/sprint2-tests/<thời điểm>/`, có summary,
`test-results.json`, `test-output.txt`, `case-results.json`, bảng độ phủ và danh sách
ca chưa đạt. Lệnh trả exit code 1 khi có kiểm tra FAIL.

Runner chạy 14 bài Sprint 2 và 4 bài component hồi quy liên quan. Output ghi commit,
hash nguồn và lệnh thực tế. Các bản minh chứng đã nộp được giữ nguyên; lượt chạy mới
được lưu riêng để đối chiếu.

Các bài test mới bám kết quả mong đợi của backlog. Chúng có thể FAIL trên code hiện
tại cho đến khi Dev sửa #id, điều hướng và nội dung hướng dẫn. Không sửa code sản phẩm
chỉ để biến bộ test thành PASS.
