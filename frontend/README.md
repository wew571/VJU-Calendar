# Frontend cho DEMO_CP_SAT

Giao diện React + Vite, dùng **design system VJU** đồng bộ với app Nhập học
(`D:\App Nhập Học\Project\BE_Enrollment`): Tailwind v4 + shadcn/ui, đỏ chủ đạo
`#D82827`, font Roboto, topbar + sidebar 2 cấp. Gắn với backend thuật toán CP-SAT
ở `../webapp/scheduler_core.py` (không sửa file đó).

Chi tiết quá trình chuyển giao diện, các quyết định và chỗ cố ý không migrate:
xem `../REFACTOR-UI-VJU.md`.

## Chạy thử (2 tiến trình)

**Terminal 1 — backend Flask (API + thuật toán):**
```
cd ../webapp
py app.py
```
Chạy tại `http://127.0.0.1:5055`.

**Terminal 2 — frontend Vite:**
```
npm install   # chỉ cần lần đầu
npm run dev
```
Mở cổng do Vite in ra (thường là `http://localhost:5173`). Với cấu hình ví dụ trong `../README.md` mục 6, `/api/*` được Vite proxy sang Flask; `vite.config.js` đọc proxy từ `../config/frontend.json`, không cần cấu hình CORS ở backend. Nếu file này thiếu, Vite tạo file rỗng rồi dừng; điền JSON hợp lệ trước khi chạy lại. `npm run build`, `npm run preview` và `npm test` cũng cần file này.

## Cấu trúc

**Lớp giao diện dùng chung** (port từ BE_Enrollment, giữ nguyên từng class):
- `src/app.css` — token VJU + cầu nối shadcn ↔ Tailwind v4. **Điểm vào CSS duy nhất**:
  nó tự kéo `styles.css` vào layer `legacy`. Đừng import `styles.css` từ `main.jsx` —
  reset `*{margin:0;padding:0}` trong đó sẽ nằm ngoài cascade layer và đè chết mọi
  utility padding/margin của Tailwind.
- `src/components/ui/*.jsx` — 15 primitive shadcn (`button`, `card`, `dialog`, `table`…).
  Hai cái **không có** ở reference: `native-select` (select gốc cho bộ chọn bắt buộc có
  giá trị) và `drawer` (ngăn kéo phải cho form dài).
- `src/components/shared/*.jsx` — `panel`, `pill`, `notice`, `list-search`,
  `filter-select`, `form-row`…
- `src/components/layout/*.jsx` — `app-topbar`, `app-sidebar` (2 cấp), `app-layout`.

**Lớp nghiệp vụ:**
- `src/context/AppDataContext.jsx` — giữ dữ liệu đang làm việc (data/guestResult/
  residentResult), gương lại `STATE` phía Flask. Nạp lại cả hai khi mở app.
- `src/services/schedulerService.js` — gọi các endpoint `/api/*`.
- `src/adapters/*.js` — chuyển dữ liệu từ `scheduler_core.py` sang prop shape các
  component cần (ngày/tiết, lesson, conflict, khung giờ đã chọn).
- `src/presentation/pages/*.jsx` — các màn hình; điều hướng khai ở `constants/nav.js`.

## Điều hướng

Sidebar 2 cấp (`constants/nav.js`): mục đơn **Thời khoá biểu** ở trên cùng, rồi
**Chuẩn bị dữ liệu** (Giảng viên), **Dữ liệu học phần**, **Nhật ký & bản lưu**
(Nhật ký thao tác · Bản đã lưu). Các mục được hiển thị theo hồ sơ vai trò;
màn nhập/sửa học phần hiện chưa được phân cho vai trò nào trong yêu cầu nghiệp vụ.

Hai màn cần toàn bộ bề ngang — Thời khoá biểu (lưới tuần) và Dữ liệu học phần (bảng
mirror 29 cột Excel) — làm sidebar **tự thu về rail 64px**. Thu gọn tự động này KHÔNG
ghi `localStorage`: nếu ghi, rời trang rộng người dùng sẽ thấy sidebar thu gọn ở mọi
trang khác mà không hiểu tại sao.

## Hồ sơ nghiệp vụ mô phỏng (không có tài khoản thật)

Màn chọn vai trò chỉ điều chỉnh menu và luồng thao tác trên trình duyệt, không xác
thực người dùng và không bảo vệ API:
- **GĐCT** (`gdct`): quản lý giảng viên thỉnh giảng và xếp lịch trong CTĐT được chọn.
- **ĐPCT** (`dpct`): quản lý hồ sơ/giờ có thể dạy của giảng viên thỉnh giảng; không xếp lịch.
- **Trợ lý khoa** (`assistant`): quản lý giảng viên thỉnh giảng, cập nhật giờ rảnh cơ hữu,
  xếp lịch toàn trường.
- **Giảng viên cơ hữu** (`resident`): khai giờ rảnh cho hồ sơ được chọn trong bản demo.
- **Xem thôi** (`viewer`): chỉ tra cứu lịch và nhật ký.

Tên CTĐT và nhóm điều phối viên hiển thị được lấy từ dữ liệu hiện có; không dùng số
lượng CTĐT hoặc nhóm điều phối viên hardcode.
Hồ sơ giảng viên thỉnh giảng trong dữ liệu hiện chưa gắn CTĐT, nên danh sách hồ sơ
dùng chung; thao tác hồ sơ chưa thể giới hạn theo CTĐT của GĐCT/ĐPCT. Vai trò chỉ
lọc giao diện, không xác thực người dùng hay bảo vệ API.

## Ghi chú

- **Dark mode chưa bật.** Token `.dark` được giữ theo reference nhưng không có gì
  kích hoạt — CSS thủ công còn lại chưa có bản dark, bật lên sẽ hỏng nửa vời.
  Lý do đầy đủ ghi ở đầu `src/app.css`.
- **CSS thủ công còn lại** (`src/styles.css`, ~1.6k dòng) chỉ phục vụ những chỗ cố ý
  không migrate: lưới thời khoá biểu, bảng nhiệt dùng chung, bảng mirror Excel.
