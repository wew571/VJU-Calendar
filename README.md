# 📅 VJU-Calendar — Hệ Thống Hỗ Trợ Xếp Thời Khóa Biểu Tự Động

> **Chào mừng bạn đến với dự án VJU-Calendar!**  
> Tài liệu này được biên soạn dành cho các thành viên mới trong đội ngũ phát triển, thầy cô giáo vụ và người dùng muốn tìm hiểu, vận hành hoặc tiếp tục hoàn thiện hệ thống xếp thời khóa biểu của Trường Đại học Việt Nhật (VJU).

---

## 🎯 1. Mục Tiêu Của Dự Án

Việc xếp thời khóa biểu thủ công cho hàng trăm lớp học phần mỗi kỳ luôn là một bài toán rất phức tạp và tốn nhiều thời gian. Giáo vụ phải cân đối rất nhiều điều kiện:
- **Giảng viên thỉnh giảng** chỉ rảnh vào một số khung giờ cố định.
- **Giảng viên cơ hữu** cần phân bổ lịch dạy hợp lý.
- **Sinh viên cùng một lớp/ngành** không thể học 2 môn cùng một lúc.
- **Phòng học** có giới hạn về số lượng, sức chứa và phân bố ở các cơ sở khác nhau.

**VJU-Calendar** ra đời nhằm:
1. **Tự động hóa tính toán:** Ứng dụng "bộ não" giải toán thông minh để tìm ra phương án xếp lịch tối ưu chỉ trong vài giây đến vài phút.
2. **Hỗ trợ điều phối linh hoạt (Bán tự động):** Cho phép giáo vụ dễ dàng kéo-thả, chỉnh sửa thủ công và hệ thống sẽ tự động cảnh báo nếu phát sinh trùng lịch.
3. **Tiết kiệm thời gian & Hạn chế sai sót:** Nhập dữ liệu trực tiếp từ file Excel kế hoạch giảng dạy và xuất ra bảng thời khóa biểu hoàn chỉnh, sẵn sàng sử dụng.

---

## 🏗️ 2. Cấu Trúc Hệ Thống (Dễ hiểu)

Hệ thống được chia thành 2 phần chính hoạt động phối hợp với nhau:

```mermaid
graph LR
    User([👤 Người dùng / Giáo vụ])
    
    subgraph Frontend ["🖥️ Giao diện Web (Frontend)"]
        UI[Trang web hiển thị lịch, kéo thả, bảng biểu]
    end
    
    subgraph Backend ["⚙️ Bộ xử lý & Thuật toán (Backend)"]
        API[Máy chủ tiếp nhận yêu cầu Flask]
        Core[Bộ não tính toán & Xếp lịch tự động CP-SAT]
        Excel[Xử lý đọc / xuất file Excel]
    end
    
    User <-->|Thao tác trực quan| UI
    UI <-->|Gửi & Nhận dữ liệu| API
    API <--> Core
    API <--> Excel
```

1. **Giao diện Web (Frontend - Thư mục `frontend/`):**
   - Là nơi người dùng thao tác trực tiếp: xem lưới lịch theo tuần, xem danh sách lớp, chọn giờ rảnh cho giảng viên, bấm nút tự động xếp lịch và kéo-thả để chỉnh sửa.
   - Giao diện được thiết kế hiện đại, mang tông màu đỏ đặc trưng của thương hiệu VJU.

2. **Bộ xử lý trung tâm (Backend - Thư mục `webapp/`):**
   - Nhận dữ liệu từ file Excel và lưu trữ trạng thái phiên làm việc.
   - Chứa **bộ não tính toán (Thuật toán CP-SAT)** để tự động giải quyết các ràng buộc phức tạp (không để trùng phòng, trùng giảng viên, trùng giờ sinh viên).
   - Xuất kết quả cuối cùng ra file Excel chuẩn định dạng.

---

## 🛠️ 3. Công Nghệ Sử Dụng

Dự án ưu tiên các công nghệ hiện đại, ổn định và dễ bảo trì:

| Thành phần | Công nghệ chính | Vai trò trong hệ thống |
|---|---|---|
| **Giao diện** | **React + Vite** | Giúp trang web phản hồi tức thì, mượt mà và trực quan. |
| **Kiểu dáng & Màu sắc** | **Tailwind CSS + shadcn/ui** | Tạo nên giao diện đẹp mắt, nhất quán theo phong cách nhận diện VJU. |
| **Máy chủ API** | **Python (Flask)** | Tiếp nhận các thao tác từ giao diện và điều phối các tác vụ. |
| **Bộ não giải toán** | **Google OR-Tools (CP-SAT)** | Thuật toán giải bài toán tối ưu hóa, tự động xếp lịch theo các quy tắc nghiệp vụ. |
| **Xử lý bảng tính** | **Pandas / OpenPyXL** | Đọc dữ liệu từ file Excel đầu vào và xuất file Excel kết quả. |

---

## 🔄 4. Quy Trình Hoạt Động Của Hệ Thống

Quy trình xếp lịch cơ bản trên hệ thống diễn ra qua 4 bước:

```
[Bước 1: Nạp dữ liệu] ──> Nhập file Excel kế hoạch giảng dạy vào hệ thống.
          │
          ▼
[Bước 2: Xếp Giai đoạn 1] ──> Tự động xếp lịch cho Giảng viên thỉnh giảng theo khung giờ họ đã đăng ký.
          │
          ▼
[Bước 3: Xếp Giai đoạn 2] ──> Tự động xếp tiếp Giảng viên cơ hữu & Gán phòng học phù hợp sức chứa.
          │
          ▼
[Bước 4: Tinh chỉnh & Xuất file] ──> Giáo vụ kiểm tra, kéo thả sửa tay nếu cần và xuất ra file Excel.
```

---

## 📂 5. Bản Đồ Thư Mục Dự Án

```text
VJU-Calendar/
├── frontend/                     # Giao diện React + Vite
│   ├── public/                   # Tài nguyên tĩnh
│   ├── src/
│   │   ├── adapters/             # Chuyển đổi và phân tích dữ liệu từ API
│   │   ├── components/           # Thành phần giao diện dùng chung
│   │   ├── constants/            # Hằng số của giao diện
│   │   ├── context/              # Trạng thái dùng chung của React
│   │   ├── hooks/                # React hooks
│   │   ├── lib/                  # Tiện ích frontend
│   │   ├── presentation/         # Trang, màn hình và thành phần nghiệp vụ
│   │   ├── services/             # Gọi API backend
│   │   ├── App.jsx               # Component gốc
│   │   └── main.jsx              # Điểm khởi tạo React
│   ├── package.json              # Dependencies và script npm
│   └── vite.config.js            # Cấu hình Vite và proxy API
├── webapp/                       # Backend Python Flask
│   ├── api/                      # Các endpoint HTTP
│   ├── domain/                   # Quy tắc và xử lý nghiệp vụ
│   ├── app.py                    # Điểm khởi động Flask
│   ├── app_config.py             # Đọc và kiểm tra config.json
│   ├── config.json               # Cấu hình cục bộ, không được Git theo dõi
│   ├── scheduler_core.py         # Mô hình xếp lịch CP-SAT
│   ├── state.py                  # Trạng thái phiên làm việc
│   ├── snapshot.py               # Lưu và khôi phục dữ liệu nhập tay
│   ├── fate_import.py            # Đọc và chuẩn hóa Excel
│   ├── fate_export.py            # Xuất dữ liệu Excel
│   ├── fate_export_luoi.py       # Xuất lưới thời khóa biểu
│   ├── fate_audit.py             # Kiểm tra dữ liệu Excel
│   ├── fate_lecturers.py         # Đọc danh sách giảng viên
│   ├── kiem_tra_pham_vi.py       # Kiểm tra xếp lịch theo phạm vi
│   ├── kiem_tra_chuyen_di.py     # Kiểm tra tối ưu di chuyển
│   ├── kiem_tra_nhom_sinh_vien.py # Kiểm tra trùng lịch sinh viên
│   └── requirements.txt          # Dependencies Python
├── doc/                          # Tài liệu dự án
│   ├── PHAN-TICH-RANG-BUOC.md
│   ├── QUY-TRINH-NGHIEP-VU-XEP-TKB.md
│   ├── HUONG_DAN_SU_DUNG.docx
│   └── run.md                    # Hướng dẫn chạy và kiểm tra chuyên sâu
├── check_real_fate_data.py       # Công cụ kiểm tra dữ liệu thực
├── .gitignore                    # Danh sách file Git bỏ qua
└── README.md                     # Tài liệu tổng quan
```

---

## 🚀 6. Hướng Dẫn Khởi Chạy (Dành Cho Người Mới)

### Yêu cầu chuẩn bị
Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt:
- **Python** (phiên bản 3.10 trở lên)
- **Node.js** (phiên bản 18 trở lên)

---

### Bước 1: Cài đặt thư viện (Chỉ cần làm lần đầu tiên)

Mở cửa sổ dòng lệnh (Terminal / Command Prompt / PowerShell) và chạy:

**1. Cài đặt thư viện Backend (Python):**
```bash
cd webapp
py -m pip install -r requirements.txt
```

**2. Cài đặt thư viện Frontend (Node.js):**
```bash
cd ../frontend
npm install
```

---

### Bước 2: Chạy chương trình

Tùy vào mục đích sử dụng, bạn có thể chọn 1 trong 2 cách sau:

#### 🔹 Cách 1: Dành cho người dùng trải nghiệm (Gọn nhẹ - 1 cửa sổ)
Cách này phù hợp khi bạn chỉ muốn chạy hệ thống để sử dụng ngay mà không chỉnh sửa mã nguồn giao diện.

```bash
# 1. Đóng gói giao diện (nếu có thay đổi)
cd frontend
npm run build

# 2. Chạy máy chủ
cd ../webapp
py app.py
```
👉 Sau đó mở trình duyệt web và truy cập địa chỉ: **`http://127.0.0.1:5055`**

---

#### 🔹 Cách 2: Dành cho lập trình viên phát triển (2 cửa sổ)
Cách này giúp giao diện tự động cập nhật ngay khi bạn sửa code (Hot-Reload).

- **Cửa sổ dòng lệnh 1 (Chạy Backend):**
  ```bash
  cd webapp
  py app.py
  ```
  *(Backend sẽ lắng nghe tại cổng `5055`)*

- **Cửa sổ dòng lệnh 2 (Chạy Frontend):**
  ```bash
  cd frontend
  npm run dev
  ```
  *(Mở đường link do Vite in ra trên màn hình, ví dụ: `http://localhost:5173`)*

> 💡 **Mẹo nhỏ:** Nếu cổng 5173 bị chương trình khác chiếm dụng, Vite sẽ tự động chuyển sang cổng 5174 hoặc 5175. Bạn chỉ cần mở đúng link mà terminal hiển thị.

---

### Bước 3: Thiết lập `config.json`

Backend đọc cấu hình từ `webapp/config.json`. File này chứa các tham số lịch học,
số phòng, giới hạn ngày dạy, khối ca theo cơ sở và cấu hình CP-SAT. File đã được
đưa vào `.gitignore`, vì vậy mỗi máy phải có một bản cấu hình riêng.

Nếu chạy backend lần đầu mà chưa có file, hệ thống sẽ:

1. Tự tạo `webapp/config.json` trống.
2. Dừng khởi động và yêu cầu người dùng nhận cấu hình từ người cung cấp hệ thống.
3. Sau khi điền cấu hình hợp lệ, chạy lại `py app.py`.

Có thể chủ động tạo file trước lần chạy đầu tiên. Nội dung mặc định hiện tại:

```json
{
  "calendar": {
    "numDays": 7,
    "slotsPerDay": 13,
    "defaultDuration": 2,
    "maxImportedPeriod": 16,
    "dayLabels": [
      "Thứ 2",
      "Thứ 3",
      "Thứ 4",
      "Thứ 5",
      "Thứ 6",
      "Thứ 7",
      "Chủ nhật"
    ],
    "slotDayNames": [
      "Thu 2",
      "Thu 3",
      "Thu 4",
      "Thu 5",
      "Thu 6",
      "Thu 7",
      "Chu nhat"
    ]
  },
  "rooms": {
    "ltPool": 60,
    "labPool": 40
  },
  "teacherDayLimits": {
    "GUEST": 5,
    "RESIDENT": 4
  },
  "campuses": {
    "priority": [
      "hoa lac",
      "my dinh"
    ],
    "sessionBlocks": {
      "hoa lac": [
        [2, 5],
        [6, 13]
      ],
      "my dinh": [
        [1, 5],
        [6, 13]
      ]
    }
  },
  "solver": {
    "timeLimitSeconds": 30,
    "numSearchWorkers": 8,
    "crossProgramCombinationLimit": 5000
  },
  "legacyDataParams": {
    "seed": 0,
    "pctPreSubmitted": 100,
    "numForcedConflicts": 0
  }
}
```

Các nhóm tham số chính:

- `calendar`: số ngày, số tiết mỗi ngày, thời lượng mặc định, tiết nhập tối đa và nhãn ngày.
- `rooms`: số phòng lý thuyết (`ltPool`) và thực hành (`labPool`) có thể dùng đồng thời.
- `teacherDayLimits`: ngày cuối cùng hệ thống được tự xếp; chỉ số bắt đầu từ `0`
  (`GUEST: 5` là Thứ 7, `RESIDENT: 4` là Thứ 6).
- `campuses.priority`: thứ tự ưu tiên gom số ngày di chuyển tới từng cơ sở.
- `campuses.sessionBlocks`: các khoảng tiết mà một buổi học phải nằm trọn bên trong.
- `solver`: giới hạn thời gian, số luồng tìm kiếm và ngưỡng tổ hợp kiểm tra sơ bộ.
- `legacyDataParams`: các trường tương thích với cấu trúc dữ liệu cũ.

Sau khi thay đổi `config.json`, cần khởi động lại backend để nạp cấu hình mới.
Không đưa file cấu hình thật vào Git.

---

## ✨ 7. Các Tính Năng Nổi Bật

1. **Lưới Thời Khóa Biểu Trực Quan:** Xem lịch học theo dạng tuần, lọc theo từng Giảng viên, từng Phòng học hoặc từng Chương trình đào tạo.
2. **Kéo - Thả Điều Chỉnh:** Cho phép giáo vụ di chuyển ca học trực tiếp trên lưới lịch.
3. **Cảnh Báo Xung Đột Tức Thì:** Tự động phát hiện và cảnh báo màu đỏ nếu phát sinh trùng giờ giảng viên hoặc trùng phòng.
4. **Xếp Lịch Linh Hoạt Theo Phạm Vi:** Có thể xếp lịch cho toàn trường hoặc xếp riêng cho từng Chương trình đào tạo / Khóa sinh viên.
5. **Hoàn Tác (Undo / Redo):** Dễ dàng quay lại trạng thái trước đó nếu lỡ thao tác nhầm.
6. **Kiểm Tra Lỗi File Excel:** Tự động chỉ ra các dòng dữ liệu bị thiếu hoặc trùng lặp mã lớp ngay khi tải file lên.

---

## 🤝 8. Hỗ Trợ & Đóng Góp

- Nếu gặp sự cố trong quá trình cài đặt hoặc vận hành, bạn có thể kiểm tra thêm tài liệu chi tiết tại:
  - `doc/run.md`: Hướng dẫn kỹ thuật và lệnh kiểm thử sâu.
  - `doc/QUY-TRINH-NGHIEP-VU-XEP-TKB.md`: Quy trình nghiệp vụ đào tạo chi tiết.
- Chúc bạn có trải nghiệm làm việc hiệu quả và thuận lợi cùng **VJU-Calendar**! 🎉