# Prompt tập trung cấu hình backend và frontend vào thư mục `config/`

> Đây là prompt hoàn chỉnh dành cho AI Agent. Agent phải khảo sát lại codebase trước khi triển khai, không được chỉ thay chuỗi đường dẫn một cách máy móc.

## Prompt

```text
Bạn là một AI Agent chuyên phát triển phần mềm. Hãy phân tích codebase hiện tại và triển khai việc tập trung cấu hình backend và frontend vào thư mục `config/` ở thư mục gốc dự án.

# 1. Bối cảnh

Dự án hiện có cấu hình backend tại `webapp/config.json`. Cấu hình frontend chưa có file JSON riêng; các giá trị phục vụ Vite dev server, đặc biệt API proxy, đang được khai báo trực tiếp trong `frontend/vite.config.js`.

Hiện trạng đã biết tại thời điểm viết yêu cầu:

- `webapp/app_config.py` khai báo `CONFIG_PATH` trỏ đến `webapp/config.json`, đọc và validate cấu hình khi import module.
- Nếu file backend không tồn tại, `webapp/app_config.py` tạo một file JSON rỗng rồi dừng khởi động bằng thông báo yêu cầu người dùng bổ sung nội dung.
- Nếu file tồn tại nhưng rỗng hoặc chứa JSON không hợp lệ, backend dừng với thông báo lỗi.
- `main.py` kiểm tra trực tiếp sự tồn tại của `webapp/config.json` trước khi khởi chạy các dịch vụ.
- `frontend/vite.config.js` đang hard-code proxy `/api` đến `http://127.0.0.1:5055` với `changeOrigin: true`.
- `README.md` mô tả vị trí và cách thiết lập `webapp/config.json`.
- `.gitignore` hiện bỏ qua `webapp/config.json`.
- Thư mục `config/` ở gốc dự án đã tồn tại nhưng chưa có file.

Agent vẫn phải tìm kiếm lại toàn bộ repository để xác nhận hiện trạng và tránh bỏ sót script, test, tài liệu hoặc tham chiếu liên quan.

# 2. Mục tiêu

Tập trung hai file cấu hình runtime vào thư mục gốc `config/`:

- Backend: chuyển `webapp/config.json` thành `config/backend.json`.
- Frontend: tạo `config/frontend.json` và chuyển các giá trị cấu hình Vite phù hợp, trước mắt gồm cấu hình API proxy đang hard-code trong `frontend/vite.config.js`, sang file này.

Sau khi hoàn tất:

1. Backend chỉ đọc `config/backend.json`.
2. Vite chỉ đọc `config/frontend.json` cho các giá trị đã được tách ra.
3. Không giữ mã migration hoặc fallback runtime về `webapp/config.json`.
4. File cấu hình thật của cả backend và frontend tiếp tục là file cục bộ, không được Git theo dõi.
5. Không tạo file cấu hình mẫu trong phạm vi công việc này.

# 3. Cấu trúc đích

Cấu trúc mong muốn:

VJU-Calendar/
├── config/
│   ├── backend.json
│   └── frontend.json
├── frontend/
│   └── vite.config.js
├── webapp/
│   └── app_config.py
├── main.py
└── ...

`config/backend.json` giữ nguyên toàn bộ nội dung và schema của `webapp/config.json` hiện tại.

`config/frontend.json` chứa cấu hình Vite đã được tách khỏi mã nguồn. Agent cần chọn schema JSON nhỏ gọn, rõ nghĩa và validate được. Schema đề xuất:

{
  "devServer": {
    "apiProxy": {
      "path": "/api",
      "target": "http://127.0.0.1:5055",
      "changeOrigin": true
    }
  }
}

Nếu codebase hoặc Vite yêu cầu schema khác hợp lý hơn, Agent phải trình bày lý do trước khi thay đổi. Không đưa secret vào frontend config vì các giá trị frontend có thể xuất hiện trong quá trình build hoặc chạy trình duyệt.

# 4. Phạm vi khảo sát bắt buộc

Trước khi chỉnh sửa, Agent phải:

1. Tìm tất cả file và tham chiếu liên quan đến:
   - `webapp/config.json`;
   - `config/backend.json`;
   - `config/frontend.json`;
   - `CONFIG_PATH`;
   - `vite.config.js`;
   - proxy `/api`, backend host và backend port;
   - thao tác đọc, ghi, tạo hoặc kiểm tra file cấu hình;
   - thông báo lỗi chứa tên hoặc đường dẫn config;
   - test và tài liệu mô tả vị trí file.
2. Kiểm tra cả file bị `.gitignore` bỏ qua nếu môi trường cho phép.
3. Xác định project root ổn định, không phụ thuộc current working directory.
4. Xác định toàn bộ luồng khởi chạy:
   - chạy `main.py`;
   - chạy trực tiếp backend từ thư mục `webapp/`;
   - chạy `npm run dev`, `npm run build`, `npm run preview` và test frontend.
5. Trình bày ngắn gọn hiện trạng, file liên quan, kế hoạch di chuyển và rủi ro trước khi sửa.

# 5. Di chuyển file thật

## 5.1. Backend

- Di chuyển nội dung hiện tại của `webapp/config.json` sang `config/backend.json` và bảo toàn nguyên vẹn JSON.
- Không thay đổi schema hoặc giá trị nghiệp vụ chỉ vì đổi vị trí và tên file.
- Nếu `config/backend.json` đã tồn tại, ưu tiên file mới.
- Nếu đồng thời tồn tại `webapp/config.json` và `config/backend.json`, giữ file mới và xóa file cũ theo yêu cầu đã xác nhận.
- Việc xóa file cũ chỉ là bước chuyển đổi repository hiện tại; không cài mã tự động xóa hoặc migration vào runtime.
- Trước thao tác di chuyển/xóa, Agent phải kiểm tra đúng hai đường dẫn mục tiêu và không được tác động đến file ngoài phạm vi.

## 5.2. Frontend

- Tạo `config/frontend.json` từ các giá trị Vite hiện đang hard-code cần đưa ra ngoài, trước mắt là API proxy.
- Cập nhật `frontend/vite.config.js` để đọc và validate file JSON này.
- Không chuyển các cấu hình kỹ thuật gắn chặt với mã nguồn nếu việc chuyển chúng không mang lại khả năng cấu hình thực tế, ví dụ plugin React, plugin Tailwind, alias source và cấu hình Vitest; chỉ tách các giá trị runtime/dev-server phù hợp.
- Không để lại bản sao hard-code của `target` hoặc `changeOrigin` làm nguồn cấu hình thứ hai.

# 6. Xác định đường dẫn

- Backend luôn sử dụng `<project-root>/config/backend.json`.
- Frontend luôn sử dụng `<project-root>/config/frontend.json`.
- Đường dẫn phải được suy ra từ vị trí file nguồn/project root, không dựa vào current working directory.
- Chuẩn hóa đường dẫn theo API đường dẫn của ngôn ngữ đang dùng.
- `main.py`, backend và Vite phải xác định cùng một project root; không được để launcher kiểm tra một file nhưng tiến trình con lại đọc file khác.
- Không hard-code đường dẫn tuyệt đối theo máy lập trình viên.
- Phải hoạt động trên Windows, Linux và macOS.
- Không log nội dung config hoặc giá trị nhạy cảm; chỉ được hiển thị đường dẫn đã resolve khi cần báo lỗi.

# 7. Hành vi khi file chưa tồn tại

Áp dụng cùng một nguyên tắc cho backend và frontend:

1. Nếu file cấu hình cần dùng chưa tồn tại, tạo file rỗng tại đúng đường dẫn đã resolve.
2. Nếu thư mục cha chưa tồn tại, tạo thư mục cha cần thiết trước khi tạo file.
3. Sau khi tạo file rỗng, dừng tiến trình hiện tại; không tiếp tục chạy với config rỗng.
4. Thông báo rõ:
   - file nào vừa được tạo;
   - file đang rỗng;
   - người dùng cần bổ sung nội dung hợp lệ trước khi chạy lại.
5. Không ghi đè file đã tồn tại.
6. Nếu không thể tạo thư mục hoặc file vì quyền truy cập/lỗi filesystem, dừng và báo lỗi gốc có ngữ cảnh đường dẫn.
7. Dùng cơ chế tạo độc quyền hoặc kiểm tra tương đương để hạn chế ghi đè khi có nhiều tiến trình khởi động đồng thời.

Hành vi này phải đúng trong các luồng:

- Chạy `main.py`: kiểm tra cả backend và frontend trước khi khởi chạy tiến trình con. Nếu thiếu file nào, tạo file rỗng tương ứng rồi dừng. Nếu cả hai cùng thiếu, ưu tiên tạo cả hai file rỗng trong một lượt rồi báo đầy đủ danh sách để người dùng không phải chạy lại nhiều lần chỉ để phát hiện file còn thiếu.
- Chạy trực tiếp backend: `webapp/app_config.py` vẫn tự xử lý thiếu `backend.json` theo quy tắc trên.
- Chạy trực tiếp lệnh Vite: `frontend/vite.config.js` tự xử lý thiếu `frontend.json` theo quy tắc trên.

# 8. Validation và xử lý lỗi

## 8.1. Backend

- Giữ nguyên toàn bộ validation hiện có trong `webapp/app_config.py`, bao gồm `availabilityGenerator`.
- Chỉ thay đổi cách xác định đường dẫn và thông báo liên quan.
- Phân biệt rõ: thiếu file, file rỗng, JSON sai cú pháp, thiếu trường và giá trị không hợp lệ.
- Không âm thầm thay backend config sai bằng giá trị mặc định.

## 8.2. Frontend

`frontend/vite.config.js` phải validate tối thiểu:

- Root JSON là object.
- `devServer.apiProxy` là object.
- `path` là chuỗi không rỗng và phù hợp làm khóa proxy.
- `target` là URL HTTP/HTTPS hợp lệ, không rỗng.
- `changeOrigin` là boolean.

Nếu file frontend rỗng, JSON sai cú pháp, thiếu trường hoặc sai kiểu:

- Dừng Vite với thông báo chỉ rõ đường dẫn cấu hình và trường lỗi.
- Không âm thầm quay lại giá trị hard-code vì hành vi đó che giấu lỗi cấu hình.
- Không sửa hoặc ghi đè nội dung file sai.

Nếu schema đề xuất được điều chỉnh, validation và test phải được điều chỉnh đồng bộ.

# 9. Cập nhật các vị trí liên quan

Agent phải khảo sát và cập nhật ít nhất:

## 9.1. `webapp/app_config.py`

- Đổi `CONFIG_PATH` sang đường dẫn cố định `<project-root>/config/backend.json`.
- Giữ nguyên luồng nạp và validation nghiệp vụ.
- Cập nhật logic tạo thư mục/file khi thiếu.
- Cập nhật mọi thông báo lỗi sang tên và đường dẫn mới.

## 9.2. `frontend/vite.config.js`

- Xác định đường dẫn cố định `<project-root>/config/frontend.json` ổn định.
- Đọc JSON bằng API Node.js sẵn có, không thêm dependency chỉ để đọc config.
- Validate trước khi tạo Vite config.
- Dùng các giá trị đã đọc để cấu hình proxy.
- Bảo đảm config được đọc đúng ở dev/build/test; nếu một command không cần proxy nhưng vẫn nạp `vite.config.js`, hành vi yêu cầu file phải nhất quán và được ghi rõ trong README.

## 9.3. `main.py`

- Kiểm tra backend và frontend theo hai đường dẫn cố định trong thư mục `config/`.
- Tạo tất cả file còn thiếu dưới dạng rỗng rồi dừng trước khi cài dependency hoặc khởi chạy dịch vụ nếu có thể sắp xếp luồng an toàn như vậy.
- Cập nhật thông báo hướng dẫn.

## 9.4. `.gitignore`

- Xóa dòng cũ `webapp/config.json`.
- Thêm đúng hai dòng:
  - `config/backend.json`
  - `config/frontend.json`
- Không ignore toàn bộ thư mục `config/`.
- Không tạo file example trong phạm vi này.

## 9.5. Cập nhật tài liệu sau khi hoàn thành phần triển khai chính

Sau khi code, file config, `.gitignore` và test đã được cập nhật, Agent phải sửa tài liệu dựa trên hành vi thực tế cuối cùng. Không được cập nhật tài liệu theo giả định trước khi xác minh thay đổi hoạt động.

### 9.5.1. `README.md` — Phần 5

Cập nhật đúng mục `## 📂 5. Bản Đồ Thư Mục Dự Án`:

- Thêm thư mục gốc `config/` cùng hai file `backend.json` và `frontend.json` vào cây thư mục.
- Mô tả ngắn gọn vai trò của từng file.
- Xóa `webapp/config.json` khỏi cây thư mục.
- Sửa mô tả `webapp/app_config.py` để nêu rõ nó đọc và kiểm tra `config/backend.json`.
- Sửa mô tả `frontend/vite.config.js` để nêu rõ nó đọc cấu hình proxy từ `config/frontend.json`.
- Giữ nguyên các mục không liên quan và bảo đảm cây thư mục phản ánh đúng repository sau khi triển khai.

### 9.5.2. `README.md` — Phần 6

Cập nhật đúng mục `## 🚀 6. Hướng Dẫn Khởi Chạy (Dành Cho Người Mới)`:

- Giữ các hướng dẫn cài dependency và cách chạy còn chính xác; chỉ điều chỉnh lệnh hoặc thứ tự nếu code sau triển khai thực sự yêu cầu.
- Thay phần thiết lập `webapp/config.json` bằng hướng dẫn cho cả:
  - `config/backend.json`;
  - `config/frontend.json`.
- Giải thích nội dung và mục đích của từng file bằng ngôn ngữ phù hợp với người mới.
- Mô tả chính xác hành vi khi thiếu một hoặc cả hai file: hệ thống tạo file rỗng, dừng và yêu cầu bổ sung nội dung hợp lệ trước khi chạy lại.
- Nêu rõ hai file nằm cố định trong `config/` ở project root và đều bị Git bỏ qua.
- Cung cấp nội dung/schema ví dụ an toàn cho `frontend.json` theo schema thực tế đã triển khai.
- Với ví dụ backend config, không sao chép dữ liệu nhạy cảm từ file thật; chỉ giữ hoặc cập nhật ví dụ an toàn hiện có.
- Hướng dẫn cách chạy lại bằng `main.py`, chạy trực tiếp backend và chạy Vite sau khi hai file hợp lệ.
- Cập nhật phần giải thích từng tham số nếu tên file hoặc đường dẫn được nhắc lại trong phần 6.
- Xóa mọi hướng dẫn hiện hành yêu cầu người dùng đặt config tại `webapp/config.json`.

### 9.5.3. `doc/run.md`

Cập nhật `doc/run.md` sau khi README phần 5 và 6 đã nhất quán:

- Thêm mục chuẩn bị cấu hình trước các cách chạy, mô tả `config/backend.json` và `config/frontend.json`.
- Mô tả hành vi tạo file rỗng và dừng khi config bị thiếu trong từng luồng `main.py`, chạy backend trực tiếp và chạy Vite trực tiếp.
- Cập nhật phần Vite proxy: `/api/*` vẫn được Vite proxy đến backend, nhưng giá trị proxy được đọc từ `config/frontend.json`, không còn khai báo trực tiếp làm nguồn cấu hình trong `vite.config.js`.
- Cập nhật các lệnh build/dev nếu hành vi nạp frontend config ảnh hưởng đến chúng.
- Bổ sung lỗi thường gặp cho file config thiếu, rỗng, JSON sai cú pháp hoặc sai schema, kèm hướng dẫn xử lý ngắn gọn.
- Trong phần `Dữ liệu nằm ở đâu`, phân biệt rõ file dữ liệu runtime trong `webapp/` với hai file cấu hình trong `config/`; không mô tả tất cả chúng như cùng nằm trong `webapp/`.
- Xóa hoặc sửa mọi tham chiếu hiện hành đến vị trí config cũ và mọi mô tả proxy không còn đúng.
- Không thay đổi các hướng dẫn nghiệp vụ, kiểm tra solver hoặc dữ liệu không liên quan.

### 9.5.4. Kiểm tra chéo tài liệu

- Đối chiếu `README.md` phần 5, phần 6 và `doc/run.md` với code thực tế sau triển khai.
- Tìm kiếm lại `webapp/config.json`, `config.json`, proxy target và tên hai file mới trong tài liệu để phát hiện nội dung lỗi thời hoặc mâu thuẫn.
- Không sao chép secret hoặc nội dung nhạy cảm từ backend config thật vào tài liệu.
- Với tài liệu lịch sử hoặc prompt cũ, chỉ sửa nếu nó đang được dùng như hướng dẫn thực thi; không xuyên tạc lịch sử thay đổi.

# 10. Chính sách Git và bảo mật

- `config/backend.json` và `config/frontend.json` là file runtime cục bộ và đều bị `.gitignore` bỏ qua.
- Không tạo file mẫu được Git theo dõi trong công việc này.
- Không dùng `git add -f` để đưa hai file config thật vào repository.
- Không log nội dung config.
- Không đặt secret vào frontend config.
- Nếu backend config hiện có dữ liệu nhạy cảm, chỉ di chuyển cục bộ; không sao chép nội dung vào test, README, prompt hoặc output báo cáo.

# 11. Kiểm thử bắt buộc

Bổ sung hoặc cập nhật test để xác minh tối thiểu:

## 11.1. Đường dẫn

1. Backend luôn trỏ đến `<project-root>/config/backend.json`.
2. Frontend luôn trỏ đến `<project-root>/config/frontend.json`.
3. Đường dẫn vẫn đúng khi chạy từ project root, `webapp/`, `frontend/` hoặc working directory khác.
4. `main.py` và từng tiến trình con resolve cùng một đường dẫn.
5. Không có code path nào đọc backend hoặc frontend config từ vị trí thay thế.

## 11.2. File thiếu và file lỗi

1. Thiếu thư mục cha thì tạo được thư mục và file rỗng.
2. Thiếu cả hai file khi chạy `main.py` thì tạo cả hai file rỗng rồi dừng với thông báo đầy đủ.
3. Chạy trực tiếp backend khi thiếu file thì tạo backend file rỗng rồi dừng.
4. Chạy trực tiếp Vite khi thiếu file thì tạo frontend file rỗng rồi dừng.
5. File đã tồn tại không bị ghi đè.
6. File rỗng bị từ chối với thông báo rõ ràng.
7. JSON sai cú pháp bị từ chối mà không bị sửa nội dung.
8. Lỗi quyền hoặc filesystem có thông báo chứa ngữ cảnh đường dẫn.

## 11.3. Backend

1. Nội dung backend hợp lệ tại vị trí mới được đọc và validate thành công.
2. JSON thiếu trường hoặc sai giá trị vẫn bị từ chối theo validation hiện có.
3. Các test `availabilityGenerator` và phần phụ thuộc config hiện tại vẫn vượt qua.
4. Không còn fallback runtime đến `webapp/config.json`.

## 11.4. Frontend

1. `frontend.json` hợp lệ tạo đúng cấu hình Vite proxy.
2. Thiếu `devServer.apiProxy`, `path`, `target` hoặc `changeOrigin` bị từ chối rõ ràng.
3. `target` sai URL và `changeOrigin` sai kiểu bị từ chối.
4. `npm run dev`, `npm run build` và test frontend nạp config theo hành vi đã tài liệu hóa.
5. Không còn giá trị proxy target hard-code làm nguồn fallback trong `vite.config.js`.

Test không được đọc, ghi, xóa hoặc sửa trực tiếp file cấu hình thật của người dùng. Sử dụng thư mục tạm, dependency injection, mock hoặc cơ chế test hiện có.

# 12. Trình tự triển khai

Agent cần thực hiện theo thứ tự an toàn:

1. Khảo sát và báo cáo hiện trạng.
2. Xác nhận schema frontend đề xuất có thể dùng với Vite hiện tại.
3. Chuẩn bị thay đổi code và test để đọc đường dẫn mới.
4. Di chuyển file backend thật sang `config/backend.json`.
5. Tạo `config/frontend.json` với các giá trị proxy hiện tại.
6. Nếu file mới đã tồn tại, ưu tiên file mới và xóa file cũ `webapp/config.json` theo yêu cầu.
7. Không giữ mã migration/fallback runtime sau khi chuyển đổi.
8. Cập nhật `.gitignore`.
9. Chạy test backend, test frontend, lint/typecheck nếu có và build frontend.
10. Sau khi phần triển khai chính vượt qua kiểm tra, cập nhật `README.md` phần 5, phần 6 và `doc/run.md` theo mục 9.5.
11. Đối chiếu tài liệu với code thực tế và tìm kiếm lại repository để bảo đảm không còn tham chiếu runtime hoặc hướng dẫn lỗi thời.
12. Báo cáo file đã thay đổi, file đã di chuyển/xóa, quyết định kỹ thuật và kết quả kiểm tra.

# 13. Ràng buộc

- Không thay đổi nội dung nghiệp vụ của backend config.
- Không làm mất backend config trong quá trình di chuyển.
- Không commit hai file config thật.
- Không giữ hai nguồn backend config hoạt động song song.
- Không để frontend vừa đọc JSON vừa có fallback hard-code cho cùng giá trị.
- Không thêm dependency mới nếu thư viện chuẩn Python/Node.js đã đáp ứng được.
- Không hard-code đường dẫn tuyệt đối.
- Không phụ thuộc current working directory.
- Không sửa chức năng nghiệp vụ không liên quan.
- Không xóa file nào ngoài `webapp/config.json` đã được xác nhận trong yêu cầu này.
- Nếu phát hiện thêm config runtime có mục đích khác, báo cáo trước khi di chuyển; không tự động gom mọi file tên `config.json`.

# 14. Tiêu chí nghiệm thu

Công việc hoàn thành khi:

- Backend luôn dùng `config/backend.json`.
- Frontend/Vite luôn dùng `config/frontend.json`.
- Không có cơ chế ghi đè hoặc đường dẫn cấu hình thay thế.
- `webapp/config.json` không còn tồn tại sau khi di chuyển thành công.
- Không có mã migration hoặc fallback runtime về file cũ.
- Nếu file mới và file cũ từng cùng tồn tại, file mới được giữ và file cũ được xóa theo yêu cầu.
- Thiếu file sẽ tạo file rỗng đúng vị trí rồi dừng, áp dụng cho cả backend và frontend.
- `main.py` tạo đủ các file đang thiếu trong một lượt rồi dừng.
- File rỗng hoặc sai không được coi là cấu hình hợp lệ và không bị âm thầm thay thế.
- Vite proxy lấy `path`, `target` và `changeOrigin` từ frontend config đã validate.
- Backend giữ nguyên schema và validation hiện có.
- `.gitignore` bỏ đường dẫn cũ và ignore đúng hai file mới, không ignore toàn bộ thư mục.
- `README.md` phần 5 hiển thị đúng cấu trúc `config/`, không còn liệt kê `webapp/config.json`.
- `README.md` phần 6 hướng dẫn đầy đủ cách chuẩn bị, kiểm tra và xử lý hai file config cho người mới.
- `doc/run.md` mô tả đúng vị trí hai file, nguồn cấu hình Vite proxy, hành vi file thiếu/rỗng/lỗi và phân biệt config với dữ liệu runtime trong `webapp/`.
- Ba phần tài liệu trên nhất quán với code thực tế và không còn hướng dẫn đặt config tại `webapp/config.json`.
- Test backend, test frontend và build đều vượt qua.
- Không phát sinh thay đổi ngoài phạm vi.

# 15. Cách AI Agent phản hồi

Trước khi viết code, hãy cung cấp:

1. Danh sách file và luồng xử lý liên quan.
2. Tóm tắt cách backend config và Vite config hiện đang hoạt động.
3. Phương án triển khai và schema `frontend.json` cuối cùng.
4. Cách bảo toàn file backend khi di chuyển.
5. Cách bảo đảm launcher và tiến trình con dùng cùng đường dẫn.
6. Rủi ro hoặc điểm chưa rõ còn lại, nếu có.

Chỉ bắt đầu chỉnh sửa sau khi đã hiểu rõ yêu cầu. Không hỏi lại các quyết định đã được chốt trong prompt này trừ khi codebase thực tế mâu thuẫn với giả định.

Sau khi hoàn thành, hãy cung cấp:

1. Tóm tắt thay đổi.
2. Danh sách file đã chỉnh sửa, tạo, di chuyển hoặc xóa.
3. Schema frontend config đã dùng.
4. Cách xử lý file thiếu, file rỗng và đường dẫn cố định.
5. Các quyết định kỹ thuật quan trọng.
6. Tóm tắt nội dung đã cập nhật trong `README.md` phần 5, phần 6 và `doc/run.md`.
7. Kết quả test, lint, typecheck và build.
8. Các giới hạn hoặc vấn đề còn tồn tại.
```

## Các quyết định đã xác nhận

| Nội dung | Quyết định |
|---|---|
| Cấu hình backend | Di chuyển `webapp/config.json` thành `config/backend.json` |
| Cấu hình frontend | Tạo `config/frontend.json` cho cấu hình Vite, trước mắt là API proxy |
| Tên file | `backend.json` và `frontend.json` |
| Khi thiếu file | Tạo file rỗng rồi dừng; áp dụng cho cả backend và frontend |
| Di chuyển file backend hiện tại | Agent di chuyển file thật trong lần triển khai |
| Mã migration runtime | Không giữ sau khi đã di chuyển |
| Khi file backend cũ và mới cùng tồn tại | Ưu tiên file mới và xóa file cũ |
| Git | Bỏ ignore đường dẫn cũ; ignore cả hai file mới |
| File mẫu | Không tạo |
| Phạm vi | Backend config hiện có và frontend Vite config; không tự động gom mọi file `config.json` |
| Tài liệu sau triển khai | Cập nhật `README.md` phần 5, phần 6 và `doc/run.md` theo hành vi thực tế |

## Lịch sử cập nhật

| Ngày | Nội dung |
|---|---|
| 2026-09-23 | Tạo khung prompt ban đầu dựa trên hiện trạng `webapp/config.json` |
| 2026-09-23 | Chốt hai file `backend.json`/`frontend.json`, đường dẫn cố định, quy tắc tạo file rỗng, Git ignore và cách xử lý file cũ |
| 2026-09-23 | Bổ sung yêu cầu cập nhật `README.md` phần 5, phần 6 và `doc/run.md` sau khi triển khai chính hoàn tất |
